import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from error_system import AppError
from ui import info, print_update_menu, redraw_screen, warn
from utils import ROOT_DIR, load_config, load_version_metadata

ZIP_RE = re.compile(r"^ServerGoV(\d+(?:\.\d+)+)\.zip$")
TMP_UPDATE_DIR = ROOT_DIR / ".tmp" / "update-installer"
SHORT_TMP_UPDATE_DIR = ROOT_DIR / ".tmp" / "u"
UPDATE_STATE_PATH = ROOT_DIR / ".servergo" / "update-state.json"
BACKUP_ROOT = ROOT_DIR / ".servergo" / "update-backups"
MAIN_PID_FILE = ROOT_DIR / ".servergo" / "server.pid"
API_PIDS_DIR = ROOT_DIR / ".servergo" / "api-pids"
EXCLUDED_REPLACE_NAMES = {
    ".git",
    ".venv",
    ".tmp",
    ".servergo",
    "generated-projects",
    "certs",
}


@dataclass(frozen=True)
class ReleasePackage:
    file_name: str
    version_text: str
    version_tuple: tuple[int, ...]

    @property
    def display_name(self) -> str:
        return f"ServerGo V{self.version_text}"


def update_center_menu() -> None:
    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== CENTRO DE ACTUALIZACIONES ===", clear=clear)
        print_update_menu()
        choice = _safe_input("Selecciona una opcion: ").strip()
        try:
            if choice == "1":
                show_current_version()
            elif choice == "2":
                list_versions()
            elif choice == "3":
                update_latest()
            elif choice == "4":
                version = _safe_input("Version destino (ej: ServerGo V0.1.2 o 0.1.2): ").strip()
                if version:
                    switch_to_version(version)
            elif choice == "5":
                rollback_previous()
            elif choice == "0":
                return
            else:
                warn("Opcion no valida.")
        except AppError as ex:
            warn(ex.format_message())

        if bool(cfg.get("ui", {}).get("pauseAfterAction", True)):
            _safe_input("\nPresiona ENTER para continuar...")


def show_current_version() -> None:
    meta = load_version_metadata()
    info(
        "Programa: ServerGo V{version} ({channel})".format(
            version=meta.get("version", "0.0.0"),
            channel=meta.get("channel", "dev"),
        )
    )
    if meta.get("build"):
        info(f"Build: {meta.get('build')}")

    state = _load_update_state()
    installed = str(state.get("installedRelease", "")).strip()
    if installed:
        info(f"Version instalada: {installed}")
    else:
        warn("No hay version instalada registrada por el actualizador ZIP.")

    _ensure_git_repo()
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    commit = _run_git(["rev-parse", "--short", "HEAD"]).strip()
    info(f"Repo local: branch={branch} commit={commit}")


def list_versions() -> None:
    versions = _get_remote_release_packages()
    if not versions:
        warn("No se encontraron paquetes de version en origin/update.")
        warn("Formato requerido: ServerGoVx.y.z.zip")
        return

    print("Versiones disponibles en rama update:")
    for release in versions:
        print(f" - {release.display_name}")


def update_latest() -> None:
    versions = _get_remote_release_packages()
    if not versions:
        raise AppError("SG-0004", "No hay paquetes de version en origin/update.")

    latest = versions[0]
    _install_release(latest)
    info(f"Actualizacion completada a {latest.display_name}.")
    show_current_version()


def switch_to_version(version: str) -> None:
    versions = _get_remote_release_packages()
    if not versions:
        raise AppError("SG-0004", "No hay paquetes de version en origin/update.")

    wanted = _match_release_input(version, versions)
    if not wanted:
        raise AppError("SG-0004", f"Version no encontrada: {version}")

    _install_release(wanted)
    info(f"Cambio de version completado: {wanted.display_name}")
    show_current_version()


def rollback_previous() -> None:
    backup_dirs = sorted(
        [d for d in BACKUP_ROOT.glob("*") if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not backup_dirs:
        raise AppError("SG-0004", "No hay backups locales para rollback.")

    latest_backup = backup_dirs[0]
    backup_content = latest_backup / "content"
    if not backup_content.exists():
        raise AppError("SG-0004", f"Backup invalido: {latest_backup}")

    _replace_installation_from_dir(backup_content)

    meta_path = latest_backup / "meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            previous = str(meta.get("previousRelease", "")).strip()
            _save_update_state({"installedRelease": previous})
        except json.JSONDecodeError:
            pass

    info("Rollback aplicado desde backup local.")
    show_current_version()


def _ensure_git_repo() -> None:
    git_dir = ROOT_DIR / ".git"
    if not git_dir.exists():
        raise AppError("SG-0004", "Este proyecto no es un repositorio Git.")


def _run_git(args: list[str], allow_failure: bool = False) -> str:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        raise AppError("SG-0004", f"Fallo comando git: {' '.join(command)}", result.stderr.strip())
    return result.stdout.strip()


def _run_git_bytes(args: list[str]) -> bytes:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=str(ROOT_DIR),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="ignore").strip()
        raise AppError("SG-0004", f"Fallo comando git: {' '.join(command)}", stderr)
    return result.stdout


def _get_remote_release_packages() -> list[ReleasePackage]:
    _ensure_git_repo()
    _run_git(["fetch", "origin", "update"])
    files = _run_git(["ls-tree", "-r", "--name-only", "origin/update"]).splitlines()

    packages: list[ReleasePackage] = []
    for file_name in files:
        base = Path(file_name).name
        match = ZIP_RE.match(base)
        if not match:
            continue
        version_text = match.group(1)
        version_tuple = tuple(int(x) for x in version_text.split("."))
        packages.append(ReleasePackage(file_name=base, version_text=version_text, version_tuple=version_tuple))

    packages.sort(key=lambda r: r.version_tuple, reverse=True)
    return packages


def _match_release_input(raw: str, versions: list[ReleasePackage]) -> ReleasePackage | None:
    value = raw.strip()
    if not value:
        return None

    normalized = value.lower().replace(" ", "")
    for release in versions:
        if normalized == release.file_name.lower():
            return release
        if normalized == release.version_text.lower():
            return release
        if normalized == f"servergov{release.version_text}".lower():
            return release
        if normalized == release.display_name.lower().replace(" ", ""):
            return release
    return None


def _install_release(release: ReleasePackage) -> None:
    info(f"Instalando {release.display_name} desde rama update...")
    _stop_running_processes_for_update()

    TMP_UPDATE_DIR.mkdir(parents=True, exist_ok=True)
    SHORT_TMP_UPDATE_DIR.mkdir(parents=True, exist_ok=True)
    work_dir = SHORT_TMP_UPDATE_DIR / f"{release.version_text}-{datetime.now().strftime('%y%m%d%H%M%S')}"
    extract_dir = work_dir / "extract"
    archive_path = work_dir / release.file_name
    work_dir.mkdir(parents=True, exist_ok=True)

    archive_bytes = _run_git_bytes(["show", f"origin/update:{release.file_name}"])
    archive_path.write_bytes(archive_bytes)

    try:
        _safe_extract_release_archive(archive_path, extract_dir)
    except OSError as ex:
        details = str(ex)
        if "WinError 206" in details or "demasiado largo" in details.lower() or "too long" in details.lower():
            raise AppError(
                "SG-0004",
                "No se pudo descomprimir el paquete por rutas demasiado largas.",
                "El paquete contiene rutas no validas para Windows; publica una version limpia sin .tmp/.servergo.",
            ) from ex
        raise AppError("SG-0004", "Fallo al descomprimir el paquete de actualizacion.", details) from ex

    source_dir = _detect_zip_root(extract_dir)
    try:
        backup_dir = _create_backup_before_replace(source_dir)
        _replace_installation_from_dir(source_dir)
    except OSError as ex:
        details = str(ex)
        if "WinError 32" in details or "being used by another process" in details.lower():
            raise AppError(
                "SG-0004",
                "No se pudo reemplazar la instalacion porque hay archivos en uso.",
                "Deten procesos activos de ServerGo y reintenta la actualizacion.",
            ) from ex
        raise AppError(
            "SG-0004",
            "No se pudo reemplazar la instalacion durante la actualizacion.",
            details,
        ) from ex

    _save_update_state({"installedRelease": release.display_name})
    info(f"Backup creado en: {backup_dir}")


def _detect_zip_root(extract_dir: Path) -> Path:
    children = [p for p in extract_dir.iterdir()]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extract_dir


def _safe_extract_release_archive(archive_path: Path, extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path, "r") as zip_file:
        for member in zip_file.infolist():
            raw_name = member.filename.replace("\\", "/")
            if not raw_name or raw_name.endswith("/"):
                continue

            parts = [p for p in raw_name.split("/") if p not in {"", "."}]
            if not parts:
                continue

            # Bloquea paths peligrosos o de salida del destino.
            if any(p == ".." for p in parts):
                continue

            # Excluye basura empaquetada por error para evitar recursiones y rutas largas.
            if parts[0] in EXCLUDED_REPLACE_NAMES:
                continue

            target = extract_dir.joinpath(*parts)
            target_text = str(target)
            if len(target_text) > 240:
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with zip_file.open(member, "r") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def _create_backup_before_replace(source_dir: Path) -> Path:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_ROOT / f"backup-{stamp}"
    backup_content = backup_dir / "content"
    backup_content.mkdir(parents=True, exist_ok=True)

    previous = str(_load_update_state().get("installedRelease", "")).strip()
    meta = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "previousRelease": previous,
    }
    (backup_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    for item in source_dir.iterdir():
        name = item.name
        if name in EXCLUDED_REPLACE_NAMES:
            continue

        current_path = ROOT_DIR / name
        if not current_path.exists():
            continue

        backup_path = backup_content / name
        if current_path.is_dir():
            shutil.copytree(current_path, backup_path, dirs_exist_ok=True)
        else:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current_path, backup_path)

    return backup_dir


def _replace_installation_from_dir(source_dir: Path) -> None:
    for item in source_dir.iterdir():
        name = item.name
        if name in EXCLUDED_REPLACE_NAMES:
            continue

        target = ROOT_DIR / name
        if target.exists():
            if target.is_dir():
                _remove_path_with_retries(target)
            else:
                _remove_path_with_retries(target)

        if item.is_dir():
            _copytree_with_retries(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            _copyfile_with_retries(item, target)


def _load_update_state() -> dict[str, str]:
    if not UPDATE_STATE_PATH.exists():
        return {}
    try:
        return json.loads(UPDATE_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_update_state(data: dict[str, str]) -> None:
    UPDATE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPDATE_STATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _stop_running_processes_for_update() -> None:
    stopped = 0
    pid_files: list[Path] = []
    if MAIN_PID_FILE.exists():
        pid_files.append(MAIN_PID_FILE)
    if API_PIDS_DIR.exists():
        pid_files.extend(sorted(API_PIDS_DIR.glob("*.pid")))

    for pid_file in pid_files:
        pid = _read_pid_file(pid_file)
        if not pid:
            continue
        if _kill_pid(pid):
            stopped += 1
            try:
                pid_file.unlink(missing_ok=True)
            except OSError:
                pass

    # Fallback: cerrar cualquier proceso cuyo comando/ruta apunte al workspace de ServerGo.
    extra_pids = _find_processes_using_root()
    for pid in extra_pids:
        if _kill_pid(pid):
            stopped += 1

    if stopped > 0:
        info(f"Procesos detenidos antes de actualizar: {stopped}")
        time.sleep(1.2)


def _read_pid_file(path: Path) -> int | None:
    try:
        raw = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not raw.isdigit():
        return None
    value = int(raw)
    return value if value > 0 else None


def _kill_pid(pid: int) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return False

    if os.name == "nt":
        cmd = ["taskkill", "/PID", str(pid), "/T", "/F"]
    else:
        cmd = ["kill", str(pid)]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return True
    # Si el proceso ya no existe, considerarlo detenido.
    stderr = (result.stderr or "").lower()
    stdout = (result.stdout or "").lower()
    text = f"{stdout}\n{stderr}"
    if "not found" in text or "no running instance" in text or "no existe" in text:
        return True
    return False


def _find_processes_using_root() -> list[int]:
    if os.name != "nt":
        return []
    root_text = str(ROOT_DIR).replace("\\", "\\\\")
    self_pid = os.getpid()
    command = (
        "$root='{root}';"
        "$selfPid={self_pid};"
        "$items=Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object {{ "
        "$_.ProcessId -ne $selfPid -and ("
        "($_.ExecutablePath -and $_.ExecutablePath -like ($root + '*')) -or "
        "($_.CommandLine -and $_.CommandLine -like ('*' + $root + '*'))"
        ") "
        "}} | Select-Object -ExpandProperty ProcessId;"
        "if($items){{ $items | ForEach-Object {{ $_ }} }}"
    ).format(root=root_text, self_pid=self_pid)
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    pids: list[int] = []
    for line in result.stdout.splitlines():
        raw = line.strip()
        if raw.isdigit():
            value = int(raw)
            if value > 0 and value != self_pid:
                pids.append(value)
    return sorted(set(pids))


def _remove_path_with_retries(path: Path, retries: int = 6, delay: float = 0.35) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            if not path.exists():
                return
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            return
        except PermissionError as ex:
            last_error = ex
            time.sleep(delay)
    if last_error:
        raise last_error


def _copytree_with_retries(source: Path, target: Path, retries: int = 6, delay: float = 0.35) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            shutil.copytree(source, target)
            return
        except PermissionError as ex:
            last_error = ex
            time.sleep(delay)
    if last_error:
        raise last_error


def _copyfile_with_retries(source: Path, target: Path, retries: int = 6, delay: float = 0.35) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            shutil.copy2(source, target)
            return
        except PermissionError as ex:
            last_error = ex
            time.sleep(delay)
    if last_error:
        raise last_error


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise AppError("SG-9999", "Entrada cancelada por el usuario.")

