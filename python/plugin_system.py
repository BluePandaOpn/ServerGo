import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Any

from ui import info, print_plugin_menu, redraw_screen, warn
from utils import ROOT_DIR, load_config, save_config

PLUGINS_DIR = ROOT_DIR / "plugins"


def plugin_menu() -> None:
    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== PLUGINS ===", clear=clear)
        print_plugin_menu()
        choice = _safe_input("Selecciona una opcion: ").strip()

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
        elif choice == "0":
            return
        else:
            warn("Opcion no valida.")

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
    if not any(str(p.get("id", "")).lower() == plugin_id.lower() for p in plugins):
        warn("Plugin no encontrado.")
        return
    cfg = load_config()
    current = set(str(x) for x in cfg.get("plugins", {}).get("enabled", []))
    if enabled:
        current.add(plugin_id)
    else:
        current = {x for x in current if x.lower() != plugin_id.lower()}
    cfg.setdefault("plugins", {})
    cfg["plugins"]["enabled"] = sorted(current)
    save_config(cfg)
    info(f"Plugin '{plugin_id}' {'activado' if enabled else 'desactivado'}.")


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
        timeout = int(action.get("timeoutSec", cfg.get("plugins", {}).get("defaultTimeoutSec", 120))) * 1000
        info(f"Comando plugin: {command}")
        result = subprocess.run(
            command if shell else command.split(),
            shell=shell,
            cwd=str(cwd),
            check=False,
            timeout=timeout / 1000,
        )
        if result.returncode != 0:
            warn(f"Comando finalizo con codigo {result.returncode}.")
        return
    warn(f"Tipo de accion no soportado: {atype}")


def _load_plugins() -> list[dict[str, Any]]:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    plugins: list[dict[str, Any]] = []
    for path in sorted(PLUGINS_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                continue
            if "id" not in data:
                continue
            data["_file"] = path.name
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


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise RuntimeError("Entrada cancelada por el usuario.") from None
