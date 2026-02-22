import json
import os
import shutil
import ssl
import subprocess
import time
from datetime import datetime
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

from api_manager import api_manager_menu, show_status as show_api_status, start_all_services, stop_all_services
from error_system import AppError, map_exception_to_app_error
from future_tools import future_tools_menu
from plugin_system import get_plugin_summary, plugin_menu, run_enabled_plugins
from scaffold import run_project_scaffold_wizard
from update_manager import update_center_menu
from ui import error, info, print_ops_menu, print_settings_menu, print_start_menu, redraw_screen, warn
from utils import DEFAULT_CONFIG, NODE_DIR, PID_FILE, ROOT_DIR, STATE_DIR, ensure_state_dir, load_config, save_config


def _node_command() -> str:
    node_cmd = shutil.which("node")
    if not node_cmd:
        raise RuntimeError("node no esta instalado o no esta en PATH.")
    return node_cmd


def _npm_command() -> str:
    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        raise RuntimeError("npm no esta instalado o no esta en PATH.")
    return npm_cmd


def _ensure_node_modules(node_dir: Path) -> None:
    modules_dir = node_dir / "node_modules"
    needs_install = not modules_dir.exists()
    if modules_dir.exists() and not (modules_dir / "selfsigned").exists():
        needs_install = True
    if not needs_install:
        return
    info("Verificando dependencias Node (npm install)...")
    subprocess.run([_npm_command(), "install"], cwd=node_dir, check=True)


def _read_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    raw = PID_FILE.read_text(encoding="utf-8").strip()
    if not raw.isdigit():
        return None
    return int(raw)


def _write_pid(pid: int) -> None:
    ensure_state_dir()
    PID_FILE.write_text(str(pid), encoding="utf-8")


def _clear_pid() -> None:
    if PID_FILE.exists():
        PID_FILE.unlink()


def launch_start_hub() -> None:
    cfg = load_config()
    while True:
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== ARRANQUE DE SERVIDOR ===", clear=clear)
        print_start_menu()
        choice = input("Selecciona una opcion: ").strip()
        if choice == "1":
            start_node_server()
            return
        if choice == "2":
            default_name = cfg.get("projectName", "Mi Servidor")
            default_port = int(cfg.get("defaultPort", 3000))
            scaffold_cfg = cfg.get("scaffold", {})
            default_output = str(scaffold_cfg.get("defaultOutputDir", "generated-projects"))
            default_base = (ROOT_DIR / default_output).resolve()
            run_project_scaffold_wizard(default_port, default_name, default_base, cfg)
            return
        if choice == "0":
            return
        warn("Opcion no valida.")


def _is_pid_running(pid: int) -> bool | None:
    if pid <= 0:
        return False
    if os.name == "nt":
        cmd = ["tasklist", "/FI", f"PID eq {pid}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return None
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _is_server_responding(port: int, use_https: bool = False) -> bool:
    scheme = "https" if use_https else "http"
    url = f"{scheme}://localhost:{port}/api/health"
    try:
        context = ssl._create_unverified_context() if use_https else None
        with urllib.request.urlopen(url, timeout=1.5, context=context) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def start_node_server() -> None:
    cfg = load_config()
    https_cfg = cfg.get("https", {})
    https_enabled = bool(https_cfg.get("enabled", False))
    port = str(cfg.get("defaultPort", 3000))
    node_dir = NODE_DIR

    if not node_dir.exists():
        raise RuntimeError(f"No existe directorio Node: {node_dir}")

    _ensure_node_modules(node_dir)
    current_pid = _read_pid()
    pid_running = _is_pid_running(current_pid) if current_pid else False
    if (pid_running is True) or _is_server_responding(int(port), use_https=https_enabled):
        scheme = "https" if https_enabled else "http"
        info(f"El servidor ya esta ejecutandose (PID {current_pid}).")
        info(f"URL: {scheme}://localhost:{port}/")
        return

    env = os.environ.copy()
    env["PORT"] = port
    ensure_state_dir()
    log_file = ROOT_DIR / ".servergo" / "server.log"
    startup_flags = 0
    if os.name == "nt":
        startup_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    info(f"Iniciando servidor en puerto {port}...")
    with log_file.open("a", encoding="utf-8") as out:
        process = subprocess.Popen(
            [_node_command(), "server.js"],
            cwd=node_dir,
            env=env,
            stdout=out,
            stderr=out,
            creationflags=startup_flags,
        )
    _write_pid(process.pid)
    scheme = "https" if https_enabled else "http"
    info(f"Servidor lanzado en segundo plano (PID {process.pid}).")
    info(f"Prueba en {scheme}://localhost:{port}/api/hello")
    if bool(cfg.get("autoOpenBrowser", True)):
        webbrowser.open(f"{scheme}://localhost:{port}/")
        info("Se abrio el navegador automaticamente.")
    automation_cfg = cfg.get("automation", {})
    if bool(automation_cfg.get("startAllApisWithMainServer", False)):
        info("Automatizacion: iniciando APIs registradas...")
        start_all_services()
    if bool(automation_cfg.get("runEnabledPluginsOnStart", False)):
        info("Automatizacion: ejecutando plugins activos...")
        executed = run_enabled_plugins()
        info(f"Plugins ejecutados: {executed}")


def stop_node_server() -> None:
    cfg = load_config()
    https_cfg = cfg.get("https", {})
    https_enabled = bool(https_cfg.get("enabled", False))
    port = int(cfg.get("defaultPort", 3000))
    pid = _read_pid()
    if not pid:
        if _is_server_responding(port, use_https=https_enabled):
            warn("El servidor responde, pero no hay PID guardado. Detenlo manualmente.")
        else:
            warn("No hay PID guardado. Es posible que el servidor no este corriendo.")
        return
    pid_running = _is_pid_running(pid)
    if pid_running is False:
        warn(f"El proceso PID {pid} ya no existe.")
        _clear_pid()
        return
    if pid_running is None:
        if _is_server_responding(port, use_https=https_enabled):
            warn("No se pudo validar el PID por permisos del sistema.")
            warn("El servidor sigue respondiendo y debe detenerse manualmente.")
        else:
            _clear_pid()
            warn("No se pudo validar PID y el servidor no responde. PID limpiado.")
        return

    if os.name == "nt":
        cmd = ["taskkill", "/PID", str(pid), "/T", "/F"]
    else:
        cmd = ["kill", str(pid)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"No se pudo detener el servidor: {result.stderr.strip()}")
    _clear_pid()
    info(f"Servidor detenido (PID {pid}).")


def run_python_task() -> None:
    info("Ejecutando tarea Python de ejemplo...")
    for i in range(1, 4):
        info(f"Procesando bloque {i}/3")
        time.sleep(0.2)
    info("Tarea Python finalizada correctamente.")


def show_environment_status() -> None:
    cfg = load_config()
    https_cfg = cfg.get("https", {})
    https_enabled = bool(https_cfg.get("enabled", False))
    port = cfg.get("defaultPort", 3000)
    server_pid = _read_pid()
    python_ok = shutil.which("python") is not None
    npm_ok = shutil.which("npm") is not None
    node_ok = shutil.which("node") is not None
    info(f"Proyecto: {ROOT_DIR}")
    info(f"Puerto configurado: {port}")
    info(f"HTTPS: {'ACTIVO' if https_enabled else 'INACTIVO'}")
    if https_enabled:
        info(f"Autocert: {'SI' if https_cfg.get('autoGenerateCert', True) else 'NO'} | "
             f"HTTP redirect: {'SI' if https_cfg.get('redirectHttp', True) else 'NO'} "
             f"(puerto {https_cfg.get('httpPort', 8080)})")
    info(f"Python disponible: {'SI' if python_ok else 'NO'}")
    info(f"Node disponible: {'SI' if node_ok else 'NO'}")
    info(f"npm disponible: {'SI' if npm_ok else 'NO'}")
    pid_running = _is_pid_running(server_pid) if server_pid else False
    live_health = _is_server_responding(int(port), use_https=https_enabled)
    if pid_running is True or live_health:
        scheme = "https" if https_enabled else "http"
        if server_pid:
            info(f"Servidor activo: SI (PID {server_pid})")
        else:
            info("Servidor activo: SI (PID no registrado)")
        info(f"URL principal: {scheme}://localhost:{port}/")
    else:
        info("Servidor activo: NO")
        if server_pid and pid_running is False:
            _clear_pid()
    if not npm_ok:
        warn("Instala Node.js para habilitar el servidor local.")


def configure_system() -> None:
    cfg = load_config()
    while True:
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== CONFIGURACIONES ===", clear=clear)
        info(f"Configuracion actual: nombre='{cfg['projectName']}', puerto={cfg['defaultPort']}")
        info(f"Auto navegador={'SI' if cfg.get('autoOpenBrowser', True) else 'NO'}, "
             f"animacion={cfg.get('python', {}).get('bannerDelayMs', 25)} ms")
        info(f"Limpiar pantalla={'SI' if cfg.get('ui', {}).get('clearScreenOnMenu', True) else 'NO'}, "
             f"pausa={'SI' if cfg.get('ui', {}).get('pauseAfterAction', True) else 'NO'}")
        info(f"Scaffold public={'SI' if cfg.get('scaffold', {}).get('createPublicDir', True) else 'NO'}, "
             f"logs={'SI' if cfg.get('scaffold', {}).get('createLogsDir', True) else 'NO'}")
        info(f"Carpeta proyectos: {cfg.get('scaffold', {}).get('defaultOutputDir', 'generated-projects')}")
        info(f"API Manager dir: {cfg.get('apiManager', {}).get('servicesDir', 'services')} | "
             f"runtime default: {cfg.get('apiManager', {}).get('defaultRuntime', 'node')}")
        info(f"Future backups: {cfg.get('future', {}).get('backupsDir', 'backups')} | "
             f"autoRoadmap={'SI' if cfg.get('future', {}).get('autoRoadmap', True) else 'NO'}")
        info(f"HTTPS={'SI' if cfg.get('https', {}).get('enabled', False) else 'NO'} | "
             f"autocert={'SI' if cfg.get('https', {}).get('autoGenerateCert', True) else 'NO'} | "
             f"redirect={'SI' if cfg.get('https', {}).get('redirectHttp', True) else 'NO'}")
        info(f"Automation apis={'SI' if cfg.get('automation', {}).get('startAllApisWithMainServer', False) else 'NO'} | "
             f"plugins={'SI' if cfg.get('automation', {}).get('runEnabledPluginsOnStart', False) else 'NO'}")
        info(f"Repo soporte: {cfg.get('support', {}).get('repoUrl', '(no configurado)')}")
        print_settings_menu()
        choice = input("Elige una opcion de configuracion: ").strip()

        if choice == "1":
            value = input("Nuevo nombre del proyecto: ").strip()
            if value:
                cfg["projectName"] = value
                save_config(cfg)
                info("Nombre actualizado.")
            else:
                warn("Nombre vacio, no se aplicaron cambios.")
        elif choice == "2":
            value = input("Nuevo puerto (1024-65535): ").strip()
            if value.isdigit() and 1024 <= int(value) <= 65535:
                cfg["defaultPort"] = int(value)
                save_config(cfg)
                info("Puerto actualizado.")
            else:
                warn("Puerto invalido.")
        elif choice == "3":
            current = bool(cfg.get("autoOpenBrowser", True))
            cfg["autoOpenBrowser"] = not current
            save_config(cfg)
            info(f"Auto abrir navegador: {'SI' if cfg['autoOpenBrowser'] else 'NO'}")
        elif choice == "4":
            value = input("Milisegundos por caracter (0-120): ").strip()
            if value.isdigit() and 0 <= int(value) <= 120:
                cfg.setdefault("python", {})
                cfg["python"]["bannerDelayMs"] = int(value)
                save_config(cfg)
                info("Velocidad de animacion actualizada.")
            else:
                warn("Valor invalido.")
        elif choice == "5":
            cfg.setdefault("ui", {})
            cfg["ui"]["clearScreenOnMenu"] = not bool(cfg["ui"].get("clearScreenOnMenu", True))
            save_config(cfg)
            info(f"Limpiar pantalla: {'SI' if cfg['ui']['clearScreenOnMenu'] else 'NO'}")
        elif choice == "6":
            cfg.setdefault("ui", {})
            cfg["ui"]["pauseAfterAction"] = not bool(cfg["ui"].get("pauseAfterAction", True))
            save_config(cfg)
            info(f"Pausa tras accion: {'SI' if cfg['ui']['pauseAfterAction'] else 'NO'}")
        elif choice == "7":
            cfg.setdefault("scaffold", {})
            cfg["scaffold"]["createPublicDir"] = not bool(cfg["scaffold"].get("createPublicDir", True))
            save_config(cfg)
            info(f"Crear carpeta public: {'SI' if cfg['scaffold']['createPublicDir'] else 'NO'}")
        elif choice == "8":
            cfg.setdefault("scaffold", {})
            cfg["scaffold"]["createLogsDir"] = not bool(cfg["scaffold"].get("createLogsDir", True))
            save_config(cfg)
            info(f"Crear carpeta logs: {'SI' if cfg['scaffold']['createLogsDir'] else 'NO'}")
        elif choice == "9":
            value = input("Nueva carpeta base (relativa al proyecto actual): ").strip()
            if value:
                cfg.setdefault("scaffold", {})
                cfg["scaffold"]["defaultOutputDir"] = value.replace("\\", "/")
                save_config(cfg)
                info("Carpeta base actualizada.")
            else:
                warn("Valor vacio, no se aplicaron cambios.")
        elif choice == "10":
            cfg = dict(DEFAULT_CONFIG)
            cfg["python"] = dict(DEFAULT_CONFIG.get("python", {}))
            cfg["ui"] = dict(DEFAULT_CONFIG.get("ui", {}))
            cfg["scaffold"] = dict(DEFAULT_CONFIG.get("scaffold", {}))
            cfg["apiManager"] = dict(DEFAULT_CONFIG.get("apiManager", {}))
            cfg["future"] = dict(DEFAULT_CONFIG.get("future", {}))
            cfg["plugins"] = dict(DEFAULT_CONFIG.get("plugins", {}))
            cfg["https"] = dict(DEFAULT_CONFIG.get("https", {}))
            cfg["automation"] = dict(DEFAULT_CONFIG.get("automation", {}))
            cfg["support"] = dict(DEFAULT_CONFIG.get("support", {}))
            save_config(cfg)
            info("Configuracion restaurada por defecto.")
        elif choice == "11":
            value = input("Nueva carpeta base para APIs (relativa al proyecto): ").strip()
            if value:
                cfg.setdefault("apiManager", {})
                cfg["apiManager"]["servicesDir"] = value.replace("\\", "/")
                save_config(cfg)
                info("Carpeta base del API Manager actualizada.")
            else:
                warn("Valor vacio, no se aplicaron cambios.")
        elif choice == "12":
            value = input("Runtime por defecto [node/python]: ").strip().lower()
            if value in {"node", "python"}:
                cfg.setdefault("apiManager", {})
                cfg["apiManager"]["defaultRuntime"] = value
                save_config(cfg)
                info("Runtime por defecto actualizado.")
            else:
                warn("Valor invalido.")
        elif choice == "13":
            value = input("Nueva carpeta de snapshots (relativa al proyecto): ").strip()
            if value:
                cfg.setdefault("future", {})
                cfg["future"]["backupsDir"] = value.replace("\\", "/")
                save_config(cfg)
                info("Carpeta de snapshots actualizada.")
            else:
                warn("Valor vacio, no se aplicaron cambios.")
        elif choice == "14":
            cfg.setdefault("future", {})
            cfg["future"]["autoRoadmap"] = not bool(cfg["future"].get("autoRoadmap", True))
            save_config(cfg)
            info(f"Auto roadmap: {'SI' if cfg['future']['autoRoadmap'] else 'NO'}")
        elif choice == "15":
            cfg.setdefault("https", {})
            cfg["https"]["enabled"] = not bool(cfg["https"].get("enabled", False))
            save_config(cfg)
            info(f"HTTPS: {'SI' if cfg['https']['enabled'] else 'NO'}")
        elif choice == "16":
            cfg.setdefault("https", {})
            cfg["https"]["autoGenerateCert"] = not bool(cfg["https"].get("autoGenerateCert", True))
            save_config(cfg)
            info(f"Autocert HTTPS: {'SI' if cfg['https']['autoGenerateCert'] else 'NO'}")
        elif choice == "17":
            cfg.setdefault("https", {})
            cfg["https"]["redirectHttp"] = not bool(cfg["https"].get("redirectHttp", True))
            save_config(cfg)
            info(f"Redirect HTTP->HTTPS: {'SI' if cfg['https']['redirectHttp'] else 'NO'}")
        elif choice == "18":
            value = input("Puerto HTTP para redirect (1024-65535): ").strip()
            if value.isdigit() and 1024 <= int(value) <= 65535:
                cfg.setdefault("https", {})
                cfg["https"]["httpPort"] = int(value)
                save_config(cfg)
                info("Puerto HTTP de redireccion actualizado.")
            else:
                warn("Puerto invalido.")
        elif choice == "19":
            cfg.setdefault("automation", {})
            cfg["automation"]["startAllApisWithMainServer"] = not bool(
                cfg["automation"].get("startAllApisWithMainServer", False)
            )
            save_config(cfg)
            info(
                "Auto iniciar APIs: "
                + ("SI" if cfg["automation"]["startAllApisWithMainServer"] else "NO")
            )
        elif choice == "20":
            cfg.setdefault("automation", {})
            cfg["automation"]["runEnabledPluginsOnStart"] = not bool(
                cfg["automation"].get("runEnabledPluginsOnStart", False)
            )
            save_config(cfg)
            info(
                "Auto ejecutar plugins: "
                + ("SI" if cfg["automation"]["runEnabledPluginsOnStart"] else "NO")
            )
        elif choice == "21":
            value = input("URL del repositorio (ej: https://github.com/owner/repo): ").strip()
            cfg.setdefault("support", {})
            cfg["support"]["repoUrl"] = value.rstrip("/")
            save_config(cfg)
            info("URL de repositorio actualizada.")
        elif choice == "0":
            return
        else:
            warn("Opcion no valida.")


def quick_https_setup() -> None:
    cfg = load_config()
    cfg.setdefault("https", {})
    cfg["https"]["enabled"] = True
    cfg["https"]["autoGenerateCert"] = True
    cfg["https"]["redirectHttp"] = True
    cfg["https"]["httpPort"] = int(cfg["https"].get("httpPort", 8080))
    save_config(cfg)
    info("HTTPS habilitado con configuracion recomendada.")
    info("Inicia el servidor para generar certificado local automaticamente.")


def operations_center() -> None:
    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== CENTRO DE OPERACIONES ===", clear=clear)
        print_ops_menu()
        choice = input("Selecciona una opcion: ").strip()
        if choice == "1":
            start_node_server()
            start_all_services()
            executed = run_enabled_plugins()
            info(f"Operacion completa. Plugins ejecutados: {executed}")
        elif choice == "2":
            stop_all_services()
            stop_node_server()
            info("Parada total completada.")
        elif choice == "3":
            show_environment_status()
            show_api_status()
            p = get_plugin_summary()
            info(f"Plugins: total={p['total']} | activos={p['active']}")
        elif choice == "4":
            cfg.setdefault("automation", {})
            cfg["automation"]["startAllApisWithMainServer"] = not bool(
                cfg["automation"].get("startAllApisWithMainServer", False)
            )
            cfg["automation"]["runEnabledPluginsOnStart"] = not bool(
                cfg["automation"].get("runEnabledPluginsOnStart", False)
            )
            save_config(cfg)
            info("Automatizaciones alternadas.")
            info(
                f"APIs auto={cfg['automation']['startAllApisWithMainServer']} | "
                f"Plugins auto={cfg['automation']['runEnabledPluginsOnStart']}"
            )
        elif choice == "5":
            report = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "project": cfg.get("projectName", "ServerGo"),
                "https": cfg.get("https", {}),
                "automation": cfg.get("automation", {}),
                "plugins": get_plugin_summary(),
            }
            reports_dir = STATE_DIR / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            name = datetime.now().strftime("ops-report-%Y%m%d-%H%M%S.json")
            path = reports_dir / name
            path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
            info(f"Reporte generado: {path}")
        elif choice == "0":
            return
        else:
            warn("Opcion no valida.")

        if bool(cfg.get("ui", {}).get("pauseAfterAction", True)):
            input("\nPresiona ENTER para continuar...")


def handle_choice(choice: str) -> bool:
    try:
        if choice == "1":
            launch_start_hub()
        elif choice == "2":
            stop_node_server()
        elif choice == "3":
            show_environment_status()
        elif choice == "4":
            configure_system()
        elif choice == "5":
            run_python_task()
        elif choice == "6":
            api_manager_menu()
        elif choice == "7":
            future_tools_menu()
        elif choice == "8":
            plugin_menu()
        elif choice == "9":
            operations_center()
        elif choice == "10":
            update_center_menu()
        elif choice == "0":
            info("Saliendo...")
            return False
        else:
            warn("Opcion no valida.")
    except subprocess.CalledProcessError as ex:
        app_err = AppError("SG-0002", f"Fallo un comando del sistema (codigo {ex.returncode}).", str(ex))
        error(app_err.format_message())
    except RuntimeError as ex:
        mapped = ex if isinstance(ex, AppError) else map_exception_to_app_error(ex)
        error(mapped.format_message())
    except Exception as ex:  # noqa: BLE001
        mapped = map_exception_to_app_error(ex)
        error(mapped.format_message())
    return True
