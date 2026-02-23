import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ui import info, warn
from utils import ROOT_DIR, STATE_DIR, ensure_state_dir, load_config

CATALOG_PATH = STATE_DIR / "api_services.json"
PID_DIR = STATE_DIR / "api-pids"
LOG_DIR = STATE_DIR / "api-logs"


def api_manager_menu() -> None:
    from ui import print_api_menu, redraw_screen

    while True:
        cfg = load_config()
        clear = bool(cfg.get("ui", {}).get("clearScreenOnMenu", True))
        redraw_screen(str(cfg.get("projectName", "ServerGo Platform")), "=== GESTOR APIS MULTI-PUERTO ===", clear=clear)
        print_api_menu()
        choice = _safe_input("Selecciona una opcion: ").strip()

        if choice == "1":
            create_api_service_wizard()
        elif choice == "2":
            list_services()
        elif choice == "3":
            name = _safe_input("Nombre del servicio a iniciar: ").strip()
            if name:
                start_service(name)
        elif choice == "4":
            start_all_services()
        elif choice == "5":
            name = _safe_input("Nombre del servicio a detener: ").strip()
            if name:
                stop_service(name)
        elif choice == "6":
            stop_all_services()
        elif choice == "7":
            show_status()
        elif choice == "8":
            create_multiple_services_wizard()
        elif choice == "9":
            name = _safe_input("Nombre del servicio a eliminar: ").strip()
            if name:
                delete_service(name)
        elif choice == "0":
            return
        else:
            warn("Opcion no valida.")

        if bool(cfg.get("ui", {}).get("pauseAfterAction", True)):
            _safe_input("\nPresiona ENTER para continuar...")


def create_api_service_wizard() -> None:
    cfg = load_config()
    api_cfg = cfg.get("apiManager", {})
    default_runtime = str(api_cfg.get("defaultRuntime", "node")).lower()
    services_dir_name = str(api_cfg.get("servicesDir", "services"))
    services_root = (ROOT_DIR / services_dir_name).resolve()
    services_root.mkdir(parents=True, exist_ok=True)

    print()
    info("Creacion de API de servicio")
    name = _safe_input("Nombre del servicio API: ").strip()
    if not name:
        warn("Nombre vacio.")
        return
    slug = _slugify(name)

    runtime = _safe_input(f"Runtime [node/python] ({default_runtime}): ").strip().lower() or default_runtime
    if runtime not in {"node", "python"}:
        warn("Runtime invalido.")
        return

    default_port = _suggest_port()
    port_raw = _safe_input(f"Puerto del servicio [{default_port}]: ").strip()
    port = default_port if not port_raw else int(port_raw) if port_raw.isdigit() else -1
    if port < 1024 or port > 65535:
        warn("Puerto invalido.")
        return
    if _port_in_use_in_catalog(port):
        warn(f"El puerto {port} ya esta asignado a otro servicio API.")
        return

    service_dir = services_root / slug
    if service_dir.exists() and any(service_dir.iterdir()):
        warn(f"La carpeta ya existe y no esta vacia: {service_dir}")
        return

    service_dir.mkdir(parents=True, exist_ok=True)
    if runtime == "node":
        _write_node_service(service_dir, name, port)
    else:
        _write_python_service(service_dir, name, port)

    catalog = _load_catalog()
    if any(item["name"].lower() == name.lower() for item in catalog):
        warn("Ya existe un servicio con ese nombre en el catalogo.")
        return

    catalog.append(
        {
            "name": name,
            "slug": slug,
            "runtime": runtime,
            "port": port,
            "path": str(service_dir),
            "healthPath": "/api/health",
        }
    )
    _save_catalog(catalog)
    info(f"Servicio API creado: {name}")
    info(f"Ruta: {service_dir}")
    info(f"Puerto: {port}")


def list_services() -> None:
    services = _load_catalog()
    if not services:
        warn("No hay servicios API registrados.")
        return
    print("Servicios registrados:")
    for item in services:
        print(
            f" - {item['name']} | runtime={item['runtime']} | "
            f"puerto={item['port']} | slug={item['slug']}"
        )


def start_service(name: str) -> None:
    service = _find_service(name)
    if not service:
        warn("Servicio no encontrado.")
        return
    if _is_service_running(service):
        info(f"Servicio '{service['name']}' ya esta activo.")
        return

    service_path = Path(service["path"])
    runtime = service["runtime"]
    port = int(service["port"])
    log_file = _log_file(service["slug"])
    ensure_state_dir()
    PID_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PORT"] = str(port)

    if runtime == "node":
        if not shutil.which("npm") or not shutil.which("node"):
            warn("Node/npm no disponible en PATH.")
            return
        if not (service_path / "node_modules").exists():
            info(f"Instalando dependencias npm para {service['name']}...")
            subprocess.run(["npm", "install"], cwd=service_path, check=True)
        cmd = ["node", "server.js"]
    else:
        py = shutil.which("python")
        if not py:
            warn("Python no disponible en PATH.")
            return
        cmd = [py, "server.py"]

    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    with log_file.open("a", encoding="utf-8") as out:
        process = subprocess.Popen(
            cmd,
            cwd=service_path,
            env=env,
            stdout=out,
            stderr=out,
            creationflags=flags,
        )
    _write_pid(service["slug"], process.pid)
    info(f"Servicio '{service['name']}' iniciado en puerto {port} (PID {process.pid}).")


def stop_service(name: str) -> None:
    service = _find_service(name)
    if not service:
        warn("Servicio no encontrado.")
        return
    pid = _read_pid(service["slug"])
    if not pid:
        warn(f"No hay PID para '{service['name']}'.")
        return
    result = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"] if os.name == "nt" else ["kill", str(pid)],
        capture_output=True,
        text=True,
        check=False,
    )
    _clear_pid(service["slug"])
    if result.returncode == 0:
        info(f"Servicio '{service['name']}' detenido.")
    else:
        warn(f"No se pudo confirmar detencion de '{service['name']}'. PID limpiado.")


def start_all_services() -> None:
    services = _load_catalog()
    if not services:
        warn("No hay servicios API registrados.")
        return
    for item in services:
        try:
            start_service(item["name"])
        except subprocess.CalledProcessError:
            warn(f"Fallo al iniciar '{item['name']}'.")


def stop_all_services() -> None:
    services = _load_catalog()
    if not services:
        warn("No hay servicios API registrados.")
        return
    for item in services:
        stop_service(item["name"])


def show_status() -> None:
    services = _load_catalog()
    if not services:
        warn("No hay servicios API registrados.")
        return
    print("Estado de servicios API:")
    for item in services:
        running = _is_service_running(item)
        health = _health_ok(int(item["port"]), str(item.get("healthPath", "/api/health")))
        print(
            f" - {item['name']}: puerto={item['port']} | "
            f"proceso={'ACTIVO' if running else 'INACTIVO'} | "
            f"health={'OK' if health else 'NO'}"
        )


def create_multiple_services_wizard() -> None:
    cfg = load_config()
    api_cfg = cfg.get("apiManager", {})
    default_runtime = str(api_cfg.get("defaultRuntime", "node")).lower()
    services_dir_name = str(api_cfg.get("servicesDir", "services"))
    services_root = (ROOT_DIR / services_dir_name).resolve()
    services_root.mkdir(parents=True, exist_ok=True)

    print()
    info("Creacion rapida de multiples APIs")
    base_name = _safe_input("Nombre base (ej: users-service): ").strip()
    if not base_name:
        warn("Nombre base vacio.")
        return
    count_raw = _safe_input("Cantidad de servicios [3]: ").strip()
    count = 3 if not count_raw else int(count_raw) if count_raw.isdigit() else -1
    if count <= 0 or count > 20:
        warn("Cantidad invalida (1-20).")
        return
    runtime = _safe_input(f"Runtime [node/python] ({default_runtime}): ").strip().lower() or default_runtime
    if runtime not in {"node", "python"}:
        warn("Runtime invalido.")
        return

    start_port = _suggest_port()
    port_raw = _safe_input(f"Puerto inicial [{start_port}]: ").strip()
    start_port = start_port if not port_raw else int(port_raw) if port_raw.isdigit() else -1
    if start_port < 1024 or start_port > 65535:
        warn("Puerto inicial invalido.")
        return

    created = 0
    for idx in range(1, count + 1):
        name = f"{base_name}-{idx}"
        slug = _slugify(name)
        port = start_port + (idx - 1)
        if _port_in_use_in_catalog(port):
            warn(f"Saltando {name}: puerto {port} ya existe en catalogo.")
            continue
        service_dir = services_root / slug
        if service_dir.exists() and any(service_dir.iterdir()):
            warn(f"Saltando {name}: carpeta existente {service_dir}.")
            continue
        service_dir.mkdir(parents=True, exist_ok=True)
        if runtime == "node":
            _write_node_service(service_dir, name, port)
        else:
            _write_python_service(service_dir, name, port)
        catalog = _load_catalog()
        catalog.append(
            {
                "name": name,
                "slug": slug,
                "runtime": runtime,
                "port": port,
                "path": str(service_dir),
                "healthPath": "/api/health",
            }
        )
        _save_catalog(catalog)
        created += 1

    info(f"Servicios creados: {created}/{count}")


def delete_service(name: str) -> None:
    service = _find_service(name)
    if not service:
        warn("Servicio no encontrado.")
        return
    if _is_service_running(service):
        warn("El servicio esta activo. Detenlo antes de eliminarlo.")
        return
    confirm = _safe_input(f"Confirmar eliminacion de '{service['name']}' [s/N]: ").strip().lower()
    if confirm not in {"s", "si", "y", "yes"}:
        warn("Eliminacion cancelada.")
        return

    catalog = [item for item in _load_catalog() if item["slug"] != service["slug"]]
    _save_catalog(catalog)
    _clear_pid(service["slug"])
    path = Path(service["path"])
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
    info(f"Servicio '{service['name']}' eliminado.")


def _find_service(name: str) -> dict[str, Any] | None:
    lowered = name.lower().strip()
    normalized = _slugify(lowered)
    for item in _load_catalog():
        if (
            item["name"].lower() == lowered
            or item["slug"].lower() == lowered
            or item["slug"].lower() == normalized
        ):
            return item
    return None


def _suggest_port() -> int:
    used = {int(item["port"]) for item in _load_catalog() if str(item.get("port", "")).isdigit()}
    port = 4000
    while port in used:
        port += 1
    return port


def _port_in_use_in_catalog(port: int) -> bool:
    return any(int(item.get("port", -1)) == port for item in _load_catalog())


def _health_ok(port: int, health_path: str) -> bool:
    url = f"http://localhost:{port}{health_path}"
    try:
        with urllib.request.urlopen(url, timeout=1.5) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def _is_service_running(service: dict[str, Any]) -> bool:
    pid = _read_pid(service["slug"])
    if pid and _is_pid_running(pid):
        return True
    return _health_ok(int(service["port"]), str(service.get("healthPath", "/api/health")))


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}"] if os.name == "nt" else ["ps", "-p", str(pid)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and str(pid) in result.stdout


def _load_catalog() -> list[dict[str, Any]]:
    ensure_state_dir()
    if not CATALOG_PATH.exists():
        return []
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if isinstance(data, list):
        return data
    return []


def _save_catalog(items: list[dict[str, Any]]) -> None:
    ensure_state_dir()
    with CATALOG_PATH.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=True)
        file.write("\n")


def _pid_file(slug: str) -> Path:
    return PID_DIR / f"{slug}.pid"


def _log_file(slug: str) -> Path:
    return LOG_DIR / f"{slug}.log"


def _read_pid(slug: str) -> int | None:
    path = _pid_file(slug)
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    if raw.isdigit():
        return int(raw)
    return None


def _write_pid(slug: str, pid: int) -> None:
    PID_DIR.mkdir(parents=True, exist_ok=True)
    _pid_file(slug).write_text(str(pid), encoding="utf-8")


def _clear_pid(slug: str) -> None:
    path = _pid_file(slug)
    if path.exists():
        path.unlink()


def _write_node_service(service_dir: Path, name: str, port: int) -> None:
    _write_json(
        service_dir / "package.json",
        {
            "name": _slugify(name),
            "version": "1.0.0",
            "private": True,
            "scripts": {"start": "node server.js"},
            "dependencies": {"express": "^4.21.2", "cors": "^2.8.5"},
        },
    )
    _write_file(
        service_dir / "server.js",
        f"""const express = require("express");
const cors = require("cors");

const app = express();
const PORT = Number(process.env.PORT || {port});
app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {{
  res.json({{ ok: true, name: "{name}", runtime: "node", port: PORT }});
}});

app.get("/api/info", (_req, res) => {{
  res.json({{ service: "{name}", mode: "multi-port", port: PORT }});
}});

app.listen(PORT, () => {{
  console.log(`[API] {name} escuchando en http://localhost:${{PORT}}`);
}});
""",
    )
    _write_file(
        service_dir / "run.bat",
        """@echo off
setlocal
cd /d "%~dp0"
if not exist node_modules npm install
npm start
endlocal
""",
    )
    _write_file(
        service_dir / "run.ps1",
        """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }
npm start
""",
    )


def _write_python_service(service_dir: Path, name: str, port: int) -> None:
    _write_file(
        service_dir / "server.py",
        f"""import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "{port}"))


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(200, {{"ok": True, "name": "{name}", "runtime": "python", "port": PORT}})
            return
        if self.path == "/api/info":
            self._send_json(200, {{"service": "{name}", "mode": "multi-port", "port": PORT}})
            return
        self._send_json(404, {{"ok": False, "error": "Not Found"}})


if __name__ == "__main__":
    print(f"[API] {name} escuchando en http://localhost:{{PORT}}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
""",
    )
    _write_file(
        service_dir / "run.bat",
        """@echo off
setlocal
cd /d "%~dp0"
python server.py
endlocal
""",
    )
    _write_file(
        service_dir / "run.ps1",
        """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python server.py
""",
    )


def _slugify(name: str) -> str:
    raw = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in raw:
        raw = raw.replace("--", "-")
    return raw or "api-service"


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise RuntimeError("Entrada cancelada por el usuario.") from None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=True)
        file.write("\n")


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(content)
