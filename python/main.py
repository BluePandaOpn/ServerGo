import sys

from error_system import AppError, explain_error, map_exception_to_app_error
from api_manager import api_manager_menu
from cli import (
    handle_choice,
    operations_center,
    quick_https_setup,
    search_docs,
    start_node_server,
    stop_node_server,
)
from future_tools import future_tools_menu
from plugin_system import plugin_menu
from scaffold import run_project_scaffold_wizard
from update_manager import update_center_menu
from ui import print_banner, print_menu, redraw_screen, warn
from utils import ROOT_DIR, load_config


def _command_mode(args: list[str]) -> bool:
    if not args:
        return True
    cmd = args[0]
    try:
        if cmd == "start-server":
            start_node_server()
            return True
        if cmd == "stop-server":
            stop_node_server()
            return True
        if cmd == "status":
            return handle_choice("3")
        if cmd == "configure":
            return handle_choice("4")
        if cmd == "task":
            return handle_choice("5")
        if cmd == "apis":
            api_manager_menu()
            return True
        if cmd == "future":
            future_tools_menu()
            return True
        if cmd == "plugins":
            plugin_menu()
            return True
        if cmd == "ops":
            operations_center()
            return True
        if cmd == "update":
            update_center_menu()
            return True
        if cmd == "create-project":
            cfg = load_config()
            default_output = str(cfg.get("scaffold", {}).get("defaultOutputDir", "generated-projects"))
            run_project_scaffold_wizard(
                int(cfg.get("defaultPort", 3000)),
                str(cfg.get("projectName", "Mi Servidor")),
                (ROOT_DIR / default_output).resolve(),
                cfg,
            )
            return True
        if cmd == "https-setup":
            quick_https_setup()
            return True
        if cmd == "docs-search":
            search_docs(" ".join(args[1:]).strip())
            return True
        if cmd in {"help", "-h", "--help"}:
            print("Comandos disponibles:")
            print("  start-server   Inicia el servidor")
            print("  stop-server    Detiene el servidor")
            print("  status         Muestra estado y entorno")
            print("  configure      Abre menu de configuracion")
            print("  create-project Crea un proyecto servidor nuevo")
            print("  apis           Abre gestor de APIs multi-puerto")
            print("  future         Abre herramientas futuras")
            print("  plugins        Abre sistema de plugins")
            print("  ops            Abre centro de operaciones")
            print("  update         Abre centro de actualizaciones")
            print("  https-setup    Activa HTTPS rapido con autocert")
            print("  docs-search    Busca texto en docs/*.md")
            print("  task           Ejecuta tarea Python demo")
            print("  help           Muestra esta ayuda")
            return True
    except RuntimeError as ex:
        mapped = ex if isinstance(ex, AppError) else map_exception_to_app_error(ex)
        warn(mapped.format_message())
        warn(explain_error(mapped.code))
        return True
    except Exception as ex:  # noqa: BLE001
        mapped = map_exception_to_app_error(ex)
        warn(mapped.format_message())
        warn(explain_error(mapped.code))
        return True
    warn(f"Comando desconocido: {cmd}")
    warn("Usa 'help' para ver comandos disponibles.")
    return True


def _interactive_mode() -> None:
    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== MENU PRINCIPAL ===", clear=clear)
        print_menu()
        choice = input("Selecciona una opcion: ").strip()
        if not handle_choice(choice):
            break
        if bool(cfg.get("ui", {}).get("pauseAfterAction", True)):
            input("\nPresiona ENTER para continuar...")


def main() -> int:
    cfg = load_config()
    project_name = cfg.get("projectName", "ServerGo Platform")
    banner_delay = int(cfg.get("python", {}).get("bannerDelayMs", 35))
    print_banner(project_name, banner_delay)

    if len(sys.argv) > 1:
        args = [arg.strip().lower() if idx == 0 else arg for idx, arg in enumerate(sys.argv[1:])]
        keep_running = _command_mode(args)
        return 0 if keep_running else 0

    _interactive_mode()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AppError as ex:
        print(ex.format_message())
        raise SystemExit(1)
    except Exception as ex:  # noqa: BLE001
        mapped = map_exception_to_app_error(ex)
        print(mapped.format_message())
        print(explain_error(mapped.code))
        raise SystemExit(1)
