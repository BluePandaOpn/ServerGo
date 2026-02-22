import subprocess
from pathlib import Path

from error_system import AppError
from ui import info, print_update_menu, redraw_screen, warn
from utils import ROOT_DIR, load_config


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
                version = _safe_input("Version/tag/branch destino: ").strip()
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
    _ensure_git_repo()
    commit = _run_git(["rev-parse", "--short", "HEAD"]).strip()
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    describe = _run_git(["describe", "--tags", "--always"]).strip()
    info(f"Version actual: {describe}")
    info(f"Branch: {branch}")
    info(f"Commit: {commit}")


def list_versions() -> None:
    _ensure_git_repo()
    local_tags = _run_git(["tag", "--sort=-creatordate"]).splitlines()
    if local_tags:
        print("Tags locales:")
        for tag in local_tags[:30]:
            print(f" - {tag}")
    else:
        warn("No se encontraron tags locales.")

    remote_tags = _run_git(["ls-remote", "--tags", "origin"], allow_failure=True).splitlines()
    if remote_tags:
        print("Tags remotos (origin):")
        tags = []
        for line in remote_tags:
            parts = line.split()
            if len(parts) == 2 and "refs/tags/" in parts[1]:
                tag = parts[1].replace("refs/tags/", "")
                if tag.endswith("^{}"):
                    continue
                tags.append(tag)
        for tag in sorted(set(tags), reverse=True)[:30]:
            print(f" - {tag}")
    else:
        warn("No se pudieron listar tags remotos (sin red o sin origin).")


def update_latest() -> None:
    _ensure_git_repo()
    _run_git(["fetch", "--all", "--tags"], allow_failure=True)
    _run_git(["pull", "--ff-only"])
    info("Actualizacion a la ultima version completada.")
    show_current_version()


def switch_to_version(version: str) -> None:
    _ensure_git_repo()
    _run_git(["fetch", "--all", "--tags"], allow_failure=True)
    _run_git(["checkout", version])
    info(f"Cambio de version completado: {version}")
    show_current_version()


def rollback_previous() -> None:
    _ensure_git_repo()
    _run_git(["checkout", "-"])
    info("Rollback aplicado a referencia anterior.")
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


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise AppError("SG-9999", "Entrada cancelada por el usuario.")

