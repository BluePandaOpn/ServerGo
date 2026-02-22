import os
import sys
import time


class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


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
    print(f"{ANSI.CYAN}{ANSI.BOLD}")
    print("   _____                           _____       ")
    print("  / ____|                         / ____|      ")
    print(" | (___   ___ _ ____   _____ _ __| |  __  ___  ")
    print("  \\___ \\ / _ \\ '__\\ \\ / / _ \\ '__| | |_ |/ _ \\ ")
    print("  ____) |  __/ |   \\ V /  __/ |  | |__| | (_) |")
    print(" |_____/ \\___|_|    \\_/ \\___|_|   \\_____|\\___/ ")
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
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Arranque de servidor (asistente)")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Detener servidor actual")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Estado del servidor y entorno")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Configuraciones (facil)")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Tarea Python de ejemplo")
    print(f"{ANSI.GREEN}6){ANSI.RESET} Gestor APIs Multi-Puerto")
    print(f"{ANSI.GREEN}7){ANSI.RESET} Herramientas Futuras")
    print(f"{ANSI.GREEN}8){ANSI.RESET} Sistema de Plugins")
    print(f"{ANSI.GREEN}9){ANSI.RESET} Centro de Operaciones")
    print(f"{ANSI.GREEN}10){ANSI.RESET} Centro de Actualizaciones")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Salir")
    print()


def print_start_menu() -> None:
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Iniciar servidor local de esta plataforma")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Crear nuevo proyecto servidor (Node.js o Python)")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def print_settings_menu() -> None:
    print(f"{ANSI.BOLD}=== CONFIGURACIONES ==={ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Cambiar nombre del proyecto")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Cambiar puerto del servidor")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Activar/Desactivar auto abrir navegador")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Velocidad de animacion del banner")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Activar/Desactivar limpiar pantalla")
    print(f"{ANSI.GREEN}6){ANSI.RESET} Activar/Desactivar pausa tras accion")
    print(f"{ANSI.GREEN}7){ANSI.RESET} Activar/Desactivar carpeta public al generar")
    print(f"{ANSI.GREEN}8){ANSI.RESET} Activar/Desactivar carpeta logs al generar")
    print(f"{ANSI.GREEN}9){ANSI.RESET} Cambiar carpeta base de proyectos generados")
    print(f"{ANSI.GREEN}10){ANSI.RESET} Restaurar configuracion por defecto")
    print(f"{ANSI.GREEN}11){ANSI.RESET} Carpeta base del gestor API multi-puerto")
    print(f"{ANSI.GREEN}12){ANSI.RESET} Runtime por defecto del gestor API")
    print(f"{ANSI.GREEN}13){ANSI.RESET} Carpeta de snapshots de herramientas futuras")
    print(f"{ANSI.GREEN}14){ANSI.RESET} Activar/Desactivar auto roadmap")
    print(f"{ANSI.GREEN}15){ANSI.RESET} Activar/Desactivar HTTPS")
    print(f"{ANSI.GREEN}16){ANSI.RESET} Activar/Desactivar autocert HTTPS")
    print(f"{ANSI.GREEN}17){ANSI.RESET} Activar/Desactivar redireccion HTTP->HTTPS")
    print(f"{ANSI.GREEN}18){ANSI.RESET} Cambiar puerto HTTP de redireccion")
    print(f"{ANSI.GREEN}19){ANSI.RESET} Auto iniciar todas las APIs con servidor principal")
    print(f"{ANSI.GREEN}20){ANSI.RESET} Auto ejecutar plugins activos al iniciar")
    print(f"{ANSI.GREEN}21){ANSI.RESET} Configurar URL de repositorio soporte")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def print_api_menu() -> None:
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Crear nuevo servicio API")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Listar servicios API")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Iniciar un servicio API")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Iniciar todos los servicios API")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Detener un servicio API")
    print(f"{ANSI.GREEN}6){ANSI.RESET} Detener todos los servicios API")
    print(f"{ANSI.GREEN}7){ANSI.RESET} Estado de servicios API")
    print(f"{ANSI.GREEN}8){ANSI.RESET} Creacion rapida de multiples APIs")
    print(f"{ANSI.GREEN}9){ANSI.RESET} Eliminar servicio API")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def print_future_menu() -> None:
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Exportar snapshot de configuracion")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Restaurar ultimo snapshot")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Limpiar estado temporal")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Ver roadmap local")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Crear roadmap si no existe")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def print_plugin_menu() -> None:
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Listar todos los plugins")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Listar plugins activos")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Activar plugin")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Desactivar plugin")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Ejecutar plugin")
    print(f"{ANSI.GREEN}6){ANSI.RESET} Crear plantilla de plugin")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def print_ops_menu() -> None:
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Arranque total (servidor + APIs + plugins)")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Parada total (APIs + servidor)")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Diagnostico total")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Alternar automatizaciones")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Generar reporte operativo")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def print_update_menu() -> None:
    print(f"{ANSI.BOLD}Opciones:{ANSI.RESET}")
    print(f"{ANSI.GREEN}1){ANSI.RESET} Ver version actual")
    print(f"{ANSI.GREEN}2){ANSI.RESET} Listar versiones disponibles")
    print(f"{ANSI.GREEN}3){ANSI.RESET} Actualizar a ultima version")
    print(f"{ANSI.GREEN}4){ANSI.RESET} Cambiar a una version especifica")
    print(f"{ANSI.GREEN}5){ANSI.RESET} Rollback a referencia anterior")
    print(f"{ANSI.GREEN}0){ANSI.RESET} Volver")


def info(message: str) -> None:
    print(f"{ANSI.CYAN}[INFO]{ANSI.RESET} {message}")


def warn(message: str) -> None:
    print(f"{ANSI.YELLOW}[WARN]{ANSI.RESET} {message}")


def error(message: str) -> None:
    print(f"{ANSI.RED}[ERROR]{ANSI.RESET} {message}")
