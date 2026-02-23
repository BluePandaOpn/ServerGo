import json
import subprocess
import time
import webbrowser
from pathlib import Path
from typing import Any

from error_system import AppError
from ui import info, print_plugin_menu, redraw_screen, warn
from utils import ROOT_DIR, load_config, save_config

PLUGINS_DIR = ROOT_DIR / "plugins"
PLUGIN_MANIFEST_NAMES = {"plugin.json", "manifest.json"}
PLUGIN_BRANCH_CANDIDATES = ("Plugins", "plugins")


def plugin_menu() -> None:
    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== PLUGINS ===", clear=clear)
        print_plugin_menu()
        choice = _safe_input("Selecciona una opcion: ").strip()

        try:
            if choice == "1":
                list_plugins(show_all=True)
            elif choice == "2":
                list_plugins(show_all=False)
            elif choice == "3":
                plugin_id = _safe_input("ID del plugin a activar: ").strip()
                if plugin_id:
                    set_plugin_enabled(plugin_id, True)
            elif choice == "4":
                plugin_id = _safe_input("ID del plugin a desactivar: ").strip()
                if plugin_id:
                    set_plugin_enabled(plugin_id, False)
            elif choice == "5":
                plugin_id = _safe_input("ID del plugin a ejecutar: ").strip()
                if plugin_id:
                    run_plugin(plugin_id)
            elif choice == "6":
                scaffold_plugin_template()
            elif choice == "7":
                install_plugin_from_catalog_ui()
            elif choice == "0":
                return
            else:
                warn("Opcion no valida.")
        except AppError as ex:
            warn(ex.format_message())
        except Exception as ex:  # noqa: BLE001
            warn(f"Error inesperado en plugins: {ex}")

        if bool(cfg.get("ui", {}).get("pauseAfterAction", True)):
            _safe_input("\nPresiona ENTER para continuar...")


def list_plugins(show_all: bool = True) -> None:
    plugins = _load_plugins()
    if not plugins:
        warn("No hay plugins en la carpeta plugins/.")
        return
    enabled_set = set(_enabled_ids())
    print("Plugins detectados:")
    for plugin in plugins:
        pid = str(plugin.get("id", ""))
        enabled = pid in enabled_set
        if (not show_all) and (not enabled):
            continue
        print(
            f" - {pid} | nombre={plugin.get('name', 'sin-nombre')} | "
            f"estado={'ACTIVO' if enabled else 'INACTIVO'} | archivo={plugin.get('_file', '?')}"
        )


def set_plugin_enabled(plugin_id: str, enabled: bool) -> None:
    plugins = _load_plugins()
    target_id = plugin_id.lower()
    resolved_id = None
    for plugin in plugins:
        pid = str(plugin.get("id", ""))
        if pid.lower() == target_id:
            resolved_id = pid
            break
    if not resolved_id:
        warn("Plugin no encontrado.")
        return

    cfg = load_config()
    current = set(str(x) for x in cfg.get("plugins", {}).get("enabled", []))
    if enabled:
        current.add(resolved_id)
    else:
        current = {x for x in current if x.lower() != resolved_id.lower()}
    cfg.setdefault("plugins", {})
    cfg["plugins"]["enabled"] = sorted(current)
    save_config(cfg)
    info(f"Plugin '{resolved_id}' {'activado' if enabled else 'desactivado'}.")


def run_plugin(plugin_id: str) -> None:
    plugin = _get_plugin_by_id(plugin_id)
    if not plugin:
        warn("Plugin no encontrado.")
        return

    cfg = load_config()
    enabled_set = set(_enabled_ids())
    if str(plugin.get("id", "")) not in enabled_set:
        warn("Plugin inactivo. Activalo primero.")
        return

    actions = plugin.get("actions", [])
    if not isinstance(actions, list) or not actions:
        warn("Plugin sin acciones.")
        return

    info(f"Ejecutando plugin: {plugin.get('name', plugin.get('id', 'plugin'))}")
    for action in actions:
        _run_action(action, cfg)
    info("Ejecucion de plugin completada.")


def run_enabled_plugins() -> int:
    plugins = _load_plugins()
    if not plugins:
        return 0
    enabled = set(_enabled_ids())
    executed = 0
    for plugin in plugins:
        pid = str(plugin.get("id", ""))
        if pid in enabled:
            run_plugin(pid)
            executed += 1
    return executed


def get_plugin_summary() -> dict[str, int]:
    plugins = _load_plugins()
    enabled = set(_enabled_ids())
    total = len(plugins)
    active = sum(1 for plugin in plugins if str(plugin.get("id", "")) in enabled)
    return {"total": total, "active": active}


def scaffold_plugin_template() -> None:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    target = PLUGINS_DIR / "mi-plugin-ejemplo.json"
    if target.exists():
        warn(f"Ya existe: {target}")
        return
    template = {
        "id": "mi-plugin-ejemplo",
        "name": "Mi Plugin Ejemplo",
        "description": "Plugin de demostracion para ServerGo",
        "actions": [
            {"type": "message", "text": "Hola desde tu plugin."},
            {"type": "command", "command": "cmd /c run.bat status"},
            {"type": "url", "url": "http://localhost:3000/api/health"},
        ],
    }
    with target.open("w", encoding="utf-8") as file:
        json.dump(template, file, indent=2, ensure_ascii=True)
        file.write("\n")
    info(f"Plantilla de plugin creada: {target}")


def install_plugin_from_catalog_ui() -> None:
    catalog = _load_remote_plugin_catalog()
    if not catalog:
        warn("No se encontraron plugins en rama remota 'Plugins'.")
        warn("Asegura que existan carpetas con plugin.json en esa rama.")
        return

    selection = _select_plugin_with_pyqt(catalog)
    if not selection:
        info("Instalacion cancelada desde la interfaz.")
        return

    plugin_name = selection.get("name", selection.get("folder", "plugin"))
    info(f"Plugin seleccionado: {plugin_name}")
    info("Cerrando interfaz visual y pasando a consola...")
    _console_install_animation()
    install_path = _install_remote_plugin(selection)
    info(f"Plugin instalado en: {install_path}")
    plugin_id = str(selection.get("id", "")).strip()
    if plugin_id:
        set_plugin_enabled(plugin_id, True)


def _run_action(action: Any, cfg: dict[str, Any]) -> None:
    if not isinstance(action, dict):
        warn("Accion invalida en plugin.")
        return
    atype = str(action.get("type", "")).strip().lower()
    if atype == "message":
        text = str(action.get("text", ""))
        print(text)
        return
    if atype == "url":
        url = str(action.get("url", "")).strip()
        if not url:
            warn("Accion url sin valor.")
            return
        webbrowser.open(url)
        info(f"URL abierta: {url}")
        return
    if atype == "command":
        command = str(action.get("command", "")).strip()
        if not command:
            warn("Accion command sin valor.")
            return
        shell = bool(action.get("shell", True))
        cwd_raw = str(action.get("cwd", ".")).strip()
        cwd = (ROOT_DIR / cwd_raw).resolve() if not Path(cwd_raw).is_absolute() else Path(cwd_raw)
        timeout = int(action.get("timeoutSec", cfg.get("plugins", {}).get("defaultTimeoutSec", 120)))
        info(f"Comando plugin: {command}")
        result = subprocess.run(
            command if shell else command.split(),
            shell=shell,
            cwd=str(cwd),
            check=False,
            timeout=timeout,
        )
        if result.returncode != 0:
            warn(f"Comando finalizo con codigo {result.returncode}.")
        return
    warn(f"Tipo de accion no soportado: {atype}")


def _iter_plugin_files() -> list[Path]:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for path in sorted(PLUGINS_DIR.rglob("*.json")):
        if path.parent == PLUGINS_DIR:
            files.append(path)
            continue
        if path.name.lower() in PLUGIN_MANIFEST_NAMES:
            files.append(path)
    return files


def _load_plugins() -> list[dict[str, Any]]:
    plugins: list[dict[str, Any]] = []
    for path in _iter_plugin_files():
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                continue
            if "id" not in data:
                continue
            data["_file"] = str(path.relative_to(PLUGINS_DIR)).replace("\\", "/")
            if "actions" not in data:
                data["actions"] = []
            plugins.append(data)
        except (OSError, json.JSONDecodeError):
            continue
    return plugins


def _enabled_ids() -> list[str]:
    cfg = load_config()
    return [str(x) for x in cfg.get("plugins", {}).get("enabled", [])]


def _get_plugin_by_id(plugin_id: str) -> dict[str, Any] | None:
    needle = plugin_id.lower()
    for plugin in _load_plugins():
        if str(plugin.get("id", "")).lower() == needle:
            return plugin
    return None


def _ensure_git_repo() -> None:
    if not (ROOT_DIR / ".git").exists():
        raise AppError("SG-0004", "No se detecta repositorio Git en ServerGo.")


def _run_git(args: list[str], allow_failure: bool = False) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        raise AppError("SG-0004", f"Fallo comando git: {' '.join(args)}", result.stderr.strip())
    return result.stdout.strip()


def _run_git_bytes(args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=str(ROOT_DIR),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="ignore").strip()
        raise AppError("SG-0004", f"Fallo comando git: {' '.join(args)}", stderr)
    return result.stdout


def _detect_remote_plugin_branch() -> str | None:
    for branch in PLUGIN_BRANCH_CANDIDATES:
        _run_git(["fetch", "origin", branch], allow_failure=True)
        check = subprocess.run(
            ["git", "rev-parse", "--verify", f"origin/{branch}"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        if check.returncode == 0:
            return branch
    return None


def _load_remote_plugin_catalog() -> list[dict[str, str]]:
    _ensure_git_repo()
    branch = _detect_remote_plugin_branch()
    if not branch:
        return []

    files = _run_git(["ls-tree", "-r", "--name-only", f"origin/{branch}"]).splitlines()
    groups: dict[str, set[str]] = {}
    for rel in files:
        parts = rel.split("/")
        if len(parts) < 2:
            continue
        folder = parts[0].strip()
        if not folder:
            continue
        groups.setdefault(folder, set()).add(rel)

    catalog: list[dict[str, str]] = []
    for folder, rel_files in sorted(groups.items()):
        manifest_rel = ""
        for candidate in PLUGIN_MANIFEST_NAMES:
            path = f"{folder}/{candidate}"
            if path in rel_files:
                manifest_rel = path
                break
        if not manifest_rel:
            continue

        try:
            raw_manifest = _run_git(["show", f"origin/{branch}:{manifest_rel}"])
            data = json.loads(raw_manifest)
        except (AppError, json.JSONDecodeError):
            continue

        if not isinstance(data, dict):
            continue
        plugin_id = str(data.get("id", "")).strip()
        if not plugin_id:
            continue

        catalog.append(
            {
                "branch": branch,
                "folder": folder,
                "manifest": manifest_rel,
                "id": plugin_id,
                "name": str(data.get("name", plugin_id)).strip() or plugin_id,
                "description": str(data.get("description", "")).strip(),
                "version": str(data.get("version", "sin-version")).strip() or "sin-version",
            }
        )

    return catalog


def _select_plugin_with_pyqt(catalog: list[dict[str, str]]) -> dict[str, str] | None:
    try:
        from PyQt6 import QtCore, QtWidgets
    except ImportError as ex:
        raise AppError(
            "SG-0002",
            "PyQt6 no esta disponible para abrir el instalador visual.",
            "Instala PyQt6 en .venv: .venv\\Scripts\\python.exe -m pip install PyQt6",
        ) from ex

    class CatalogDialog(QtWidgets.QDialog):
        def __init__(self, items: list[dict[str, str]]) -> None:
            super().__init__()
            self._items = items
            self.selected: dict[str, str] | None = None
            self.setWindowTitle("ServerGo - Instalador de Plugins")
            self.setMinimumSize(980, 620)

            layout = QtWidgets.QVBoxLayout(self)
            title = QtWidgets.QLabel()
            title.setTextFormat(QtCore.Qt.TextFormat.RichText)
            title.setText(
                """
                <div style="background:#0d1b2a;color:#e0e1dd;padding:18px;border-radius:10px;">
                  <h2 style="margin:0 0 8px 0;">Catalogo de Plugins</h2>
                  <p style="margin:0;">Selecciona un plugin y pulsa <b>Instalar</b>. Al confirmar, la ventana se cierra y continua la instalacion en consola.</p>
                </div>
                """
            )
            layout.addWidget(title)

            splitter = QtWidgets.QSplitter()
            splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
            layout.addWidget(splitter, 1)

            self.list_widget = QtWidgets.QListWidget()
            self.list_widget.setAlternatingRowColors(True)
            for item in items:
                self.list_widget.addItem(f"{item['name']} ({item['id']})")
            splitter.addWidget(self.list_widget)

            self.details = QtWidgets.QTextBrowser()
            self.details.setOpenExternalLinks(False)
            splitter.addWidget(self.details)
            splitter.setStretchFactor(0, 3)
            splitter.setStretchFactor(1, 5)

            buttons = QtWidgets.QHBoxLayout()
            buttons.addStretch(1)
            self.install_btn = QtWidgets.QPushButton("Instalar")
            cancel_btn = QtWidgets.QPushButton("Cancelar")
            buttons.addWidget(self.install_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons)

            self.list_widget.currentRowChanged.connect(self._update_details)
            self.install_btn.clicked.connect(self._accept_selected)
            cancel_btn.clicked.connect(self.reject)
            self.list_widget.itemDoubleClicked.connect(lambda _: self._accept_selected())

            if items:
                self.list_widget.setCurrentRow(0)
            else:
                self.install_btn.setEnabled(False)

        def _update_details(self, row: int) -> None:
            if row < 0 or row >= len(self._items):
                self.details.setHtml("<p>Sin seleccion.</p>")
                return
            item = self._items[row]
            html = f"""
            <div style="font-family:Segoe UI;padding:8px;">
              <h3 style="margin-bottom:6px;color:#1d3557;">{item['name']}</h3>
              <p><b>ID:</b> {item['id']}</p>
              <p><b>Version:</b> {item['version']}</p>
              <p><b>Rama:</b> {item['branch']}</p>
              <p><b>Carpeta remota:</b> {item['folder']}</p>
              <hr/>
              <p>{item['description'] or 'Sin descripcion.'}</p>
            </div>
            """
            self.details.setHtml(html)

        def _accept_selected(self) -> None:
            row = self.list_widget.currentRow()
            if row < 0 or row >= len(self._items):
                return
            self.selected = self._items[row]
            self.accept()

    app = QtWidgets.QApplication.instance()
    owns_app = False
    if app is None:
        app = QtWidgets.QApplication([])
        owns_app = True

    dialog = CatalogDialog(catalog)
    result = dialog.exec()
    selection = dialog.selected if result == int(QtWidgets.QDialog.DialogCode.Accepted) else None

    if owns_app:
        app.quit()
    return selection


def _console_install_animation() -> None:
    steps = [
        "Sincronizando rama remota de plugins...",
        "Validando manifiesto del plugin...",
        "Descargando archivos del plugin...",
        "Registrando plugin localmente...",
    ]
    for step in steps:
        info(step)
        time.sleep(0.22)


def _install_remote_plugin(plugin: dict[str, str]) -> Path:
    branch = plugin["branch"]
    folder = plugin["folder"]
    prefix = f"{folder}/"
    files = _run_git(["ls-tree", "-r", "--name-only", f"origin/{branch}"]).splitlines()
    plugin_files = [f for f in files if f.startswith(prefix) and not f.endswith("/")]
    if not plugin_files:
        raise AppError("SG-0005", f"No se encontraron archivos para plugin remoto: {folder}")

    install_dir = PLUGINS_DIR / folder
    install_dir.mkdir(parents=True, exist_ok=True)

    for remote_file in plugin_files:
        relative = remote_file[len(prefix):].strip()
        if not relative:
            continue
        rel_path = Path(relative)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            warn(f"Ruta remota invalida ignorada: {remote_file}")
            continue
        local_path = install_dir / relative
        local_path.parent.mkdir(parents=True, exist_ok=True)
        file_bytes = _run_git_bytes(["show", f"origin/{branch}:{remote_file}"])
        local_path.write_bytes(file_bytes)

    return install_dir


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise RuntimeError("Entrada cancelada por el usuario.") from None
