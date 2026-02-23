import os
import sys
import time

from utils import load_version_metadata


class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


def _print_section(title: str) -> None:
    print(f"{ANSI.CYAN}{ANSI.BOLD}{title}{ANSI.RESET}")


def _print_item(key: str, label: str) -> None:
    print(f"{ANSI.GREEN}{key:>2}){ANSI.RESET} {label}")


def _print_separator() -> None:
    print(f"{ANSI.DIM}{'-' * 52}{ANSI.RESET}")


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def animate_text(text: str, delay_ms: int = 35) -> None:
    delay = max(delay_ms, 0) / 1000
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()


def print_logo() -> None:
    meta = load_version_metadata()
    version = meta.get("version", "0.0.0")
    channel = meta.get("channel", "dev")
    build = meta.get("build", "").strip()
    build_text = f" | build {build}" if build else ""
    print(f"{ANSI.CYAN}{ANSI.BOLD}")
    print("   _____                           _____       ")
    print("  / ____|                         / ____|      ")
    print(" | (___   ___ _ ____   _____ _ __| |  __  ___  ")
    print("  \\___ \\ / _ \\ '__\\ \\ / / _ \\ '__| | |_ |/ _ \\ ")
    print("  ____) |  __/ |   \\ V /  __/ |  | |__| | (_) |")
    print(" |_____/ \\___|_|    \\_/ \\___|_|   \\_____|\\___/ ")
    print(f"{ANSI.DIM}Version V{version} ({channel}){build_text}{ANSI.RESET}")
    print(f"{ANSI.RESET}")


def print_banner(project_name: str, delay_ms: int = 35) -> None:
    clear_screen()
    print_logo()
    animate_text(f"{ANSI.DIM}Iniciando {project_name}...{ANSI.RESET}", delay_ms)


def redraw_screen(project_name: str, title: str, clear: bool = True) -> None:
    if clear:
        clear_screen()
    print_logo()
    print(f"{ANSI.DIM}{project_name}{ANSI.RESET}")
    print(f"{ANSI.BOLD}{title}{ANSI.RESET}")
    print()


def print_menu() -> None:
    _print_section("ACCIONES PRINCIPALES")
    _print_item("1", "Arranque de servidor (asistente)")
    _print_item("2", "Detener servidor actual")
    _print_item("3", "Estado del servidor y entorno")
    _print_item("4", "Configuraciones")
    _print_separator()
    _print_section("HERRAMIENTAS")
    _print_item("6", "Gestor APIs Multi-Puerto")
    _print_item("7", "Herramientas Futuras")
    _print_item("8", "Sistema de Plugins")
    _print_item("9", "Centro de Operaciones")
    _print_item("10", "Centro de Actualizaciones")
    _print_separator()
    _print_section("UTILIDADES")
    _print_item("5", "Tarea Python de ejemplo")
    _print_item("0", "Salir")
    print()


def print_start_menu() -> None:
    _print_section("ARRANQUE")
    _print_item("1", "Iniciar servidor local de esta plataforma")
    _print_item("2", "Crear nuevo proyecto servidor (Node.js o Python)")
    _print_item("0", "Volver")


def print_settings_menu() -> None:
    _print_section("CONFIGURACION GENERAL")
    _print_item("1", "Cambiar nombre del proyecto")
    _print_item("2", "Cambiar puerto del servidor")
    _print_item("3", "Activar/Desactivar auto abrir navegador")
    _print_item("4", "Velocidad de animacion del banner")
    _print_item("5", "Activar/Desactivar limpiar pantalla")
    _print_item("6", "Activar/Desactivar pausa tras accion")
    _print_separator()
    _print_section("GENERADOR DE PROYECTOS")
    _print_item("7", "Activar/Desactivar carpeta public al generar")
    _print_item("8", "Activar/Desactivar carpeta logs al generar")
    _print_item("9", "Cambiar carpeta base de proyectos generados")
    _print_item("10", "Restaurar configuracion por defecto")
    _print_separator()
    _print_section("GESTORES Y BACKUPS")
    _print_item("11", "Carpeta base del gestor API multi-puerto")
    _print_item("12", "Runtime por defecto del gestor API")
    _print_item("13", "Carpeta de snapshots de herramientas futuras")
    _print_item("14", "Activar/Desactivar auto roadmap")
    _print_separator()
    _print_section("HTTPS")
    _print_item("15", "Activar/Desactivar HTTPS")
    _print_item("16", "Activar/Desactivar autocert HTTPS")
    _print_item("17", "Activar/Desactivar redireccion HTTP->HTTPS")
    _print_item("18", "Cambiar puerto HTTP de redireccion")
    _print_separator()
    _print_section("AUTOMATIZACION Y SOPORTE")
    _print_item("19", "Auto iniciar todas las APIs con servidor principal")
    _print_item("20", "Auto ejecutar plugins activos al iniciar")
    _print_item("21", "Configurar URL de repositorio soporte")
    _print_item("0", "Volver")


def print_api_menu() -> None:
    _print_section("GESTOR API")
    _print_item("1", "Crear nuevo servicio API")
    _print_item("2", "Listar servicios API")
    _print_item("3", "Iniciar un servicio API")
    _print_item("4", "Iniciar todos los servicios API")
    _print_item("5", "Detener un servicio API")
    _print_item("6", "Detener todos los servicios API")
    _print_item("7", "Estado de servicios API")
    _print_item("8", "Creacion rapida de multiples APIs")
    _print_item("9", "Eliminar servicio API")
    _print_item("0", "Volver")


def print_future_menu() -> None:
    _print_section("HERRAMIENTAS FUTURAS")
    _print_item("1", "Exportar snapshot de configuracion")
    _print_item("2", "Restaurar ultimo snapshot")
    _print_item("3", "Limpiar estado temporal")
    _print_item("4", "Ver roadmap local")
    _print_item("5", "Crear roadmap si no existe")
    _print_item("0", "Volver")


def print_plugin_menu() -> None:
    _print_section("SISTEMA DE PLUGINS")
    _print_item("1", "Listar todos los plugins")
    _print_item("2", "Listar plugins activos")
    _print_item("3", "Activar plugin")
    _print_item("4", "Desactivar plugin")
    _print_item("5", "Ejecutar plugin")
    _print_item("6", "Crear plantilla de plugin")
    _print_item("0", "Volver")


def print_ops_menu() -> None:
    _print_section("CENTRO DE OPERACIONES")
    _print_item("1", "Arranque total (servidor + APIs + plugins)")
    _print_item("2", "Parada total (APIs + servidor)")
    _print_item("3", "Diagnostico total")
    _print_item("4", "Alternar automatizaciones")
    _print_item("5", "Generar reporte operativo")
    _print_item("0", "Volver")


def print_update_menu() -> None:
    _print_section("CENTRO DE ACTUALIZACIONES")
    _print_item("1", "Ver version actual")
    _print_item("2", "Listar versiones (rama update, ZIP)")
    _print_item("3", "Actualizar a la ultima version ZIP")
    _print_item("4", "Instalar version especifica ZIP")
    _print_item("5", "Rollback desde backup local")
    _print_item("0", "Volver")


def info(message: str) -> None:
    print(f"{ANSI.CYAN}[INFO]{ANSI.RESET} {message}")


def warn(message: str) -> None:
    print(f"{ANSI.YELLOW}[WARN]{ANSI.RESET} {message}")


def error(message: str) -> None:
    print(f"{ANSI.RED}[ERROR]{ANSI.RESET} {message}")
