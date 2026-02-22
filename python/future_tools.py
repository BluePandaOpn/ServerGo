import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ui import info, warn
from utils import DEFAULT_CONFIG, ROOT_DIR, STATE_DIR, load_config, save_config
ROADMAP_PATH = ROOT_DIR / "docs" / "ROADMAP.md"


def future_tools_menu() -> None:
    from ui import print_future_menu, redraw_screen

    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== HERRAMIENTAS FUTURAS ===", clear=clear)
        print_future_menu()
        choice = _safe_input("Selecciona una opcion: ").strip()

        if choice == "1":
            export_config_snapshot()
        elif choice == "2":
            restore_latest_snapshot()
        elif choice == "3":
            cleanup_runtime_state()
        elif choice == "4":
            show_roadmap()
        elif choice == "5":
            ensure_roadmap_file()
        elif choice == "0":
            return
        else:
            warn("Opcion no valida.")

        if bool(cfg.get("ui", {}).get("pauseAfterAction", True)):
            _safe_input("\nPresiona ENTER para continuar...")


def export_config_snapshot() -> Path:
    cfg = load_config()
    backups_dir = _backups_dir(cfg)
    if bool(cfg.get("future", {}).get("autoRoadmap", True)):
        ensure_roadmap_file()
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = backups_dir / f"config-snapshot-{stamp}.json"
    with target.open("w", encoding="utf-8") as file:
        json.dump(cfg, file, indent=2, ensure_ascii=True)
        file.write("\n")
    info(f"Snapshot creado: {target}")
    return target


def restore_latest_snapshot() -> None:
    snapshots = sorted(_backups_dir(load_config()).glob("config-snapshot-*.json"))
    if not snapshots:
        warn("No hay snapshots en backups/.")
        return
    latest = snapshots[-1]
    with latest.open("r", encoding="utf-8") as file:
        loaded = json.load(file)
    merged = _merge_with_defaults(loaded)
    save_config(merged)
    info(f"Configuracion restaurada desde: {latest.name}")


def cleanup_runtime_state() -> None:
    removed = 0
    if STATE_DIR.exists():
        for path in STATE_DIR.rglob("*.pid"):
            try:
                path.unlink()
                removed += 1
            except OSError:
                pass
    tmp_dir = ROOT_DIR / ".tmp"
    if tmp_dir.exists():
        for item in tmp_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                    removed += 1
            except OSError:
                pass
    info(f"Limpieza completada. Elementos eliminados: {removed}")


def show_roadmap() -> None:
    ensure_roadmap_file()
    text = ROADMAP_PATH.read_text(encoding="utf-8")
    print(text)


def ensure_roadmap_file() -> None:
    if ROADMAP_PATH.exists():
        info(f"Roadmap disponible: {ROADMAP_PATH}")
        return
    ROADMAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    ROADMAP_PATH.write_text(
        "# ServerGo Roadmap\n\n"
        "## Proximo\n"
        "- Plantillas de deployment\n"
        "- Observabilidad basica\n"
        "- Plugin system para comandos\n\n"
        "## Mediano Plazo\n"
        "- Integracion CI local\n"
        "- UI web para administracion\n",
        encoding="utf-8",
    )
    info(f"Roadmap creado: {ROADMAP_PATH}")


def _merge_with_defaults(config: dict[str, Any]) -> dict[str, Any]:
    def merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in base.items():
            if isinstance(value, dict):
                incoming = override.get(key, {})
                result[key] = merge(value, incoming) if isinstance(incoming, dict) else value
            else:
                result[key] = override.get(key, value)
        for key, value in override.items():
            if key not in result:
                result[key] = value
        return result

    return merge(DEFAULT_CONFIG, config)


def _backups_dir(cfg: dict[str, Any]) -> Path:
    name = str(cfg.get("future", {}).get("backupsDir", "backups"))
    return (ROOT_DIR / name).resolve()


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise RuntimeError("Entrada cancelada por el usuario.") from None
