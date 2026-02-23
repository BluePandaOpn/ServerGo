import json
import re
import time
from pathlib import Path
from typing import Any

from ui import info, warn


PYTHON_STACKS = {
    "1": ("http.server (Recomendado)", "http_server"),
    "2": ("Flask", "flask"),
    "3": ("FastAPI", "fastapi"),
    "4": ("Bottle", "bottle"),
    "5": ("AioHTTP", "aiohttp"),
}


def run_project_scaffold_wizard(
    default_port: int,
    default_project_name: str,
    default_base: Path,
    global_config: dict[str, Any] | None = None,
) -> None:
    cfg = global_config or {}
    scaffold_cfg = cfg.get("scaffold", {})

    print()
    info("Asistente de creacion de proyectos servidor")
    info("Se generara un proyecto completo y organizado, listo para usar.")
    print()

    runtime_choice = _ask_choice(
        "Selecciona tecnologia base",
        {
            "1": "Node.js",
            "2": "Python",
            "0": "Cancelar",
        },
    )
    if runtime_choice == "0":
        warn("Operacion cancelada.")
        return

    project_name = _safe_input(f"Nombre del proyecto [{default_project_name}]: ").strip() or default_project_name
    project_slug = _slugify(project_name)

    base_input = _safe_input(f"Ruta base donde crearlo [{default_base}]: ").strip()
    base_dir = Path(base_input).expanduser() if base_input else default_base
    base_dir = base_dir.resolve()
    project_dir = base_dir / project_slug

    port = _ask_port(default_port)
    create_public = _ask_yes_no(
        "Crear carpeta public para HTML/CSS/JS",
        bool(scaffold_cfg.get("createPublicDir", True)),
    )
    create_logs = _ask_yes_no(
        "Crear carpeta logs del servidor",
        bool(scaffold_cfg.get("createLogsDir", True)),
    )
    create_scripts = _ask_yes_no(
        "Crear carpeta scripts con .ps1 y .bat",
        bool(scaffold_cfg.get("createScriptsDir", True)),
    )

    stack_key = "node"
    if runtime_choice == "1":
        _simulate_setup("Preparando plantilla Node.js")
    else:
        stack_choice = _ask_choice("Selecciona herramienta Python", {k: v[0] for k, v in PYTHON_STACKS.items()})
        stack_key = PYTHON_STACKS[stack_choice][1]
        _simulate_setup("Preparando plantilla Python")

    options = {
        "runtime": "node" if runtime_choice == "1" else "python",
        "python_stack": stack_key,
        "create_public": create_public,
        "create_logs": create_logs,
        "create_scripts": create_scripts,
    }
    _create_project_structure(project_dir, project_name, port, options)

    info(f"Proyecto generado en: {project_dir}")
    info("Arranque rapido: entra al proyecto y ejecuta run.bat")
    if create_scripts:
        info("Modo consola: scripts\\console.bat (salir con Ctrl+L)")


def _create_project_structure(project_dir: Path, project_name: str, port: int, options: dict[str, Any]) -> None:
    _ensure_project_dir(project_dir)

    runtime = options["runtime"]
    create_public = bool(options["create_public"])
    create_logs = bool(options["create_logs"])
    create_scripts = bool(options["create_scripts"])
    python_stack = str(options["python_stack"])

    (project_dir / "src").mkdir(parents=True, exist_ok=True)
    (project_dir / "config").mkdir(parents=True, exist_ok=True)
    (project_dir / ".servergo").mkdir(parents=True, exist_ok=True)
    if create_public:
        (project_dir / "public").mkdir(parents=True, exist_ok=True)
    if create_logs:
        (project_dir / "logs").mkdir(parents=True, exist_ok=True)
    if create_scripts:
        (project_dir / "scripts").mkdir(parents=True, exist_ok=True)

    _write_json(
        project_dir / "config" / "appsettings.json",
        {
            "projectName": project_name,
            "runtime": runtime,
            "pythonStack": python_stack if runtime == "python" else "",
            "port": port,
            "publicDir": "public" if create_public else "",
            "logsDir": "logs" if create_logs else "",
        },
    )
    _write_file(
        project_dir / ".gitignore",
        ".venv/\nnode_modules/\n__pycache__/\n*.pyc\n.servergo/server.pid\nlogs/*.log\n",
    )
    _write_file(
        project_dir / "README.md",
        _readme_template(project_name, port, runtime, python_stack, create_public, create_scripts),
    )

    if runtime == "node":
        _create_node_runtime(project_dir, project_name, port, create_public)
    else:
        _create_python_runtime(project_dir, project_name, port, python_stack, create_public)

    _create_root_launchers(project_dir)
    if create_scripts:
        _create_management_scripts(project_dir, runtime)


def _create_node_runtime(project_dir: Path, project_name: str, port: int, create_public: bool) -> None:
    _write_json(
        project_dir / "package.json",
        {
            "name": _slugify(project_name),
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "start": "node src/server.js"
            },
            "dependencies": {
                "cors": "^2.8.5",
                "express": "^4.21.2"
            },
        },
    )
    _write_file(project_dir / "src" / "server.js", _node_server_template())
    if create_public:
        _write_file(project_dir / "public" / "index.html", _index_template(project_name, runtime="Node.js"))


def _create_python_runtime(project_dir: Path, project_name: str, port: int, python_stack: str, create_public: bool) -> None:
    requirements = _python_requirements(python_stack)
    if requirements:
        _write_file(project_dir / "requirements.txt", requirements)
    _write_file(project_dir / "src" / "server.py", _python_server_template(python_stack, project_name, port, create_public))
    if create_public:
        _write_file(project_dir / "public" / "index.html", _index_template(project_name, runtime=f"Python/{python_stack}"))


def _create_root_launchers(project_dir: Path) -> None:
    _write_file(
        project_dir / "run.bat",
        """@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\\install.ps1"
if errorlevel 1 exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\\start.ps1"
endlocal
""",
    )
    _write_file(
        project_dir / "run.ps1",
        """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& "$PSScriptRoot\\scripts\\install.ps1"
& "$PSScriptRoot\\scripts\\start.ps1"
""",
    )


def _create_management_scripts(project_dir: Path, runtime: str) -> None:
    scripts = project_dir / "scripts"
    _write_file(scripts / "lib.ps1", _ps_lib_template(runtime))
    _write_file(scripts / "install.ps1", _ps_install_template(runtime))
    _write_file(scripts / "start.ps1", _ps_start_template(runtime))
    _write_file(scripts / "server-console.ps1", _ps_server_console_template())
    _write_file(scripts / "stop.ps1", _ps_stop_template())
    _write_file(scripts / "status.ps1", _ps_status_template())
    _write_file(scripts / "open.ps1", _ps_open_template())
    _write_file(scripts / "console.ps1", _ps_console_template())

    _write_file(scripts / "install.bat", _bat_wrapper("install.ps1"))
    _write_file(scripts / "start.bat", _bat_wrapper("start.ps1"))
    _write_file(scripts / "stop.bat", _bat_wrapper("stop.ps1"))
    _write_file(scripts / "status.bat", _bat_wrapper("status.ps1"))
    _write_file(scripts / "open.bat", _bat_wrapper("open.ps1"))
    _write_file(scripts / "console.bat", _bat_wrapper("console.ps1"))


def _ask_choice(title: str, options: dict[str, str]) -> str:
    while True:
        print()
        print(f"=== {title} ===")
        for key, label in options.items():
            print(f"{key}) {label}")
        value = _safe_input("Elige una opcion: ").strip()
        if value in options:
            return value
        warn("Opcion invalida.")


def _ask_port(default_port: int) -> int:
    while True:
        value = _safe_input(f"Puerto del servidor [{default_port}]: ").strip()
        if not value:
            return default_port
        if value.isdigit() and 1024 <= int(value) <= 65535:
            return int(value)
        warn("Puerto invalido. Debe estar entre 1024 y 65535.")


def _ask_yes_no(label: str, default: bool) -> bool:
    hint = "S/n" if default else "s/N"
    value = _safe_input(f"{label} [{hint}]: ").strip().lower()
    if not value:
        return default
    return value in {"s", "si", "y", "yes"}


def _slugify(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip().lower())
    cleaned = cleaned.strip("-")
    return cleaned or "mi-servidor"


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise RuntimeError("Entrada cancelada por el usuario.") from None


def _simulate_setup(title: str) -> None:
    info(title)
    for step in [
        "Validando parametros",
        "Creando estructura de carpetas",
        "Generando servidor",
        "Creando scripts de gestion",
        "Finalizando instalador",
    ]:
        print(f"  - {step}...")
        time.sleep(0.09)
    info("Plantilla lista.")


def _ensure_project_dir(project_dir: Path) -> None:
    if project_dir.exists() and any(project_dir.iterdir()):
        raise RuntimeError(f"La ruta ya existe y no esta vacia: {project_dir}")
    project_dir.mkdir(parents=True, exist_ok=True)


def _python_requirements(stack_key: str) -> str:
    if stack_key == "http_server":
        return ""
    mapping = {
        "flask": "Flask>=3.0,<4.0\n",
        "fastapi": "fastapi>=0.116,<1.0\nuvicorn>=0.35,<1.0\n",
        "bottle": "bottle>=0.13,<1.0\n",
        "aiohttp": "aiohttp>=3.10,<4.0\n",
    }
    return mapping.get(stack_key, "")


def _readme_template(
    project_name: str,
    port: int,
    runtime: str,
    python_stack: str,
    create_public: bool,
    create_scripts: bool,
) -> str:
    stack_text = runtime if runtime == "node" else f"python/{python_stack}"
    scripts_text = "scripts/*.ps1 y scripts/*.bat" if create_scripts else "sin carpeta scripts"
    public_text = "si" if create_public else "no"
    return f"""# {project_name}

Proyecto generado por ServerGo.

## Resumen

- Runtime: {stack_text}
- Puerto: {port}
- Carpeta public: {public_text}
- Gestion: {scripts_text}

## Uso

- `run.bat`
- `run.ps1`

## Scripts

- `scripts/install.bat`
- `scripts/start.bat`
- `scripts/stop.bat`
- `scripts/status.bat`
- `scripts/console.bat` (salida rapida con Ctrl+L)
"""


def _index_template(project_name: str, runtime: str) -> str:
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
    <style>
      body {{
        font-family: Segoe UI, Arial, sans-serif;
        margin: 28px;
        background: #f8fafc;
        color: #0f172a;
      }}
      code {{ color: #14532d; font-weight: 700; }}
    </style>
  </head>
  <body>
    <h1>{project_name}</h1>
    <p>Servidor generado por ServerGo.</p>
    <p>Runtime: <code>{runtime}</code></p>
    <p>Prueba: <code>/api/health</code></p>
  </body>
</html>
"""


def _node_server_template() -> str:
    return """const fs = require("fs");
const path = require("path");
const express = require("express");
const cors = require("cors");

const app = express();
const root = path.resolve(__dirname, "..");
const cfgPath = path.join(root, "config", "appsettings.json");
const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
const port = Number(process.env.PORT || cfg.port || 3000);
const publicDir = cfg.publicDir ? path.join(root, cfg.publicDir) : "";

app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {
  res.json({
    ok: true,
    runtime: "node",
    project: cfg.projectName,
    port: port
  });
});

if (publicDir && fs.existsSync(publicDir)) {
  app.use(express.static(publicDir));
}

app.listen(port, () => {
  console.log(`[NODE] ${cfg.projectName} escuchando en http://localhost:${port}`);
});
"""


def _python_server_template(stack_key: str, project_name: str, port: int, create_public: bool) -> str:
    public_path = "Path(__file__).resolve().parent.parent / 'public'"
    if stack_key == "http_server":
        return f"""import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

root = Path(__file__).resolve().parent.parent
cfg = json.loads((root / "config" / "appsettings.json").read_text(encoding="utf-8"))
port = int(cfg.get("port", {port}))
public_dir = {public_path}
if public_dir.exists():
    os.chdir(public_dir)

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"[PYTHON] {project_name} en http://localhost:{{port}}")
    server.serve_forever()
"""
    if stack_key == "flask":
        static_folder = "../public" if create_public else None
        static_line = f'app = Flask(__name__, static_folder="{static_folder}", static_url_path="")' if static_folder else "app = Flask(__name__)"
        index_route = """
@app.get("/")
def index():
    return app.send_static_file("index.html")
""" if create_public else ""
        return f"""import json
from pathlib import Path
from flask import Flask, jsonify

root = Path(__file__).resolve().parent.parent
cfg = json.loads((root / "config" / "appsettings.json").read_text(encoding="utf-8"))
port = int(cfg.get("port", {port}))

{static_line}
{index_route}

@app.get("/api/health")
def health():
    return jsonify({{"ok": True, "project": cfg.get("projectName"), "runtime": "flask", "port": port}})

if __name__ == "__main__":
    print(f"[PYTHON] {{cfg.get('projectName')}} en http://localhost:{{port}}")
    app.run(host="0.0.0.0", port=port)
"""
    if stack_key == "fastapi":
        static_mount = """
if (root / "public").exists():
    app.mount("/", StaticFiles(directory=str(root / "public"), html=True), name="public")
""" if create_public else ""
        return f"""import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

root = Path(__file__).resolve().parent.parent
cfg = json.loads((root / "config" / "appsettings.json").read_text(encoding="utf-8"))
port = int(cfg.get("port", {port}))
app = FastAPI()

@app.get("/api/health")
def health():
    return {{"ok": True, "project": cfg.get("projectName"), "runtime": "fastapi", "port": port}}
{static_mount}
if __name__ == "__main__":
    print(f"[PYTHON] {{cfg.get('projectName')}} en http://localhost:{{port}}")
    uvicorn.run(app, host="0.0.0.0", port=port)
"""
    if stack_key == "bottle":
        static_code = """
@app.get("/")
def index():
    return static_file("index.html", root=str(root / "public"))

@app.get("/<filepath:path>")
def static_files(filepath):
    return static_file(filepath, root=str(root / "public"))
""" if create_public else ""
        return f"""import json
from pathlib import Path
from bottle import Bottle, response, run, static_file

root = Path(__file__).resolve().parent.parent
cfg = json.loads((root / "config" / "appsettings.json").read_text(encoding="utf-8"))
port = int(cfg.get("port", {port}))
app = Bottle()

@app.get("/api/health")
def health():
    response.content_type = "application/json"
    return {{"ok": True, "project": cfg.get("projectName"), "runtime": "bottle", "port": port}}
{static_code}
if __name__ == "__main__":
    print(f"[PYTHON] {{cfg.get('projectName')}} en http://localhost:{{port}}")
    run(app=app, host="0.0.0.0", port=port)
"""
    static_code = """
if (root / "public").exists():
    app.router.add_static("/", str(root / "public"), show_index=True)
""" if create_public else ""
    return f"""import json
from pathlib import Path
from aiohttp import web

root = Path(__file__).resolve().parent.parent
cfg = json.loads((root / "config" / "appsettings.json").read_text(encoding="utf-8"))
port = int(cfg.get("port", {port}))

async def health(_request):
    return web.json_response({{"ok": True, "project": cfg.get("projectName"), "runtime": "aiohttp", "port": port}})

def main():
    app = web.Application()
    app.router.add_get("/api/health", health)
{static_code}
    print(f"[PYTHON] {{cfg.get('projectName')}} en http://localhost:{{port}}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
"""


def _ps_lib_template(runtime: str) -> str:
    server_cmd = "node src/server.js" if runtime == "node" else ".venv\\Scripts\\python.exe src/server.py"
    install_cmd = "npm install" if runtime == "node" else ".venv\\Scripts\\python.exe -m pip install -r requirements.txt"
    runtime_check = """
if ($cfg.runtime -eq "node") {
  if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Node no disponible." }
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm no disponible." }
} else {
  if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python no disponible." }
}
"""
    return f"""Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Script:Root = Split-Path -Parent $PSScriptRoot
$Script:StateDir = Join-Path $Script:Root ".servergo"
$Script:PidFile = Join-Path $Script:StateDir "server.pid"
$Script:CfgPath = Join-Path $Script:Root "config\\appsettings.json"
$Script:Cfg = Get-Content $Script:CfgPath -Raw | ConvertFrom-Json
$Script:Port = [int]$Script:Cfg.port
$Script:HealthUrl = "http://localhost:$($Script:Port)/api/health"
$Script:ServerCmd = "{server_cmd}"
$Script:InstallCmd = "{install_cmd}"

function Show-Logo {{
  Clear-Host
  Write-Host "   _____                           _____       " -ForegroundColor Cyan
  Write-Host "  / ____|                         / ____|      " -ForegroundColor Cyan
  Write-Host " | (___   ___ _ ____   _____ _ __| |  __  ___  " -ForegroundColor Cyan
  Write-Host "  \\___ \\ / _ \\ '__\\ \\ / / _ \\ '__| | |_ |/ _ \\ " -ForegroundColor Cyan
  Write-Host "  ____) |  __/ |   \\ V /  __/ |  | |__| | (_) |" -ForegroundColor Cyan
  Write-Host " |_____/ \\___|_|    \\_/ \\___|_|   \\_____|\\___/ " -ForegroundColor Cyan
  Write-Host ""
}}

function Write-Section([string]$Title) {{
  Write-Host "=== $Title ===" -ForegroundColor DarkCyan
}}

function Invoke-SpinnerStep([string]$Message, [int]$DurationMs = 700) {{
  $frames = @("/", "|", "\\", "-")
  $steps = [Math]::Max([int]($DurationMs / 120), 2)
  for ($i = 0; $i -lt $steps; $i++) {{
    $frame = $frames[$i % $frames.Count]
    Write-Host -NoNewline "`r[$frame] $Message   "
    Start-Sleep -Milliseconds 120
  }}
  Write-Host "`r[+] $Message     "
}}

function Invoke-SpinnerJob([string]$Message, [scriptblock]$Action) {{
  $frames = @("/", "|", "\\", "-")
  $job = Start-Job -ScriptBlock $Action
  $i = 0
  while ($job.State -eq "Running") {{
    $frame = $frames[$i % $frames.Count]
    Write-Host -NoNewline "`r[$frame] $Message   "
    Start-Sleep -Milliseconds 120
    $i++
  }}
  Wait-Job $job | Out-Null
  $state = $job.State
  $null = Receive-Job $job -Keep -ErrorAction SilentlyContinue 2>$null
  $errors = @()
  if ($job.ChildJobs.Count -gt 0) {{
    $errors = @($job.ChildJobs[0].Error | ForEach-Object {{ $_.ToString() }})
  }}
  Remove-Job $job
  if ($state -ne "Completed") {{
    Write-Host "`r[!] $Message     " -ForegroundColor Red
    if ($errors.Count -gt 0) {{ $errors | ForEach-Object {{ Write-Host $_ }} }}
    throw "Fallo en: $Message"
  }}
  Write-Host "`r[+] $Message     "
}}

function Ensure-State {{
  if (-not (Test-Path $Script:StateDir)) {{ New-Item -ItemType Directory -Path $Script:StateDir | Out-Null }}
}}

function Test-Health {{
  try {{
    $r = Invoke-WebRequest -Uri $Script:HealthUrl -UseBasicParsing -TimeoutSec 2
    return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
  }} catch {{
    return $false
  }}
}}

function Get-ServerPid {{
  if (-not (Test-Path $Script:PidFile)) {{ return $null }}
  $raw = (Get-Content $Script:PidFile -Raw).Trim()
  if ($raw -match "^\\d+$") {{ return [int]$raw }}
  return $null
}}

function Save-ServerPid([int]$ServerPid) {{
  Ensure-State
  Set-Content -Path $Script:PidFile -Value $ServerPid -Encoding UTF8
}}

function Clear-ServerPid {{
  if (Test-Path $Script:PidFile) {{ Remove-Item -Force $Script:PidFile }}
}}

function Ensure-Prerequisites {{
  {runtime_check}
}}
"""


def _ps_install_template(runtime: str) -> str:
    install_python = """
$rootPath = $Script:Root
if (-not (Test-Path ".venv\\Scripts\\python.exe")) {
  Invoke-SpinnerJob "Creando .venv de Python" {
    Set-Location $using:rootPath
    python -m venv .venv
  }
}
if (Test-Path "requirements.txt") {
  Invoke-SpinnerJob "Instalando dependencias Python" {
    Set-Location $using:rootPath
    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
  }
}
"""
    install_node = """
$rootPath = $Script:Root
if (-not (Test-Path "node_modules")) {
  Invoke-SpinnerJob "Instalando dependencias npm" {
    Set-Location $using:rootPath
    npm install
  }
}
"""
    return f"""Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Set-Location $Script:Root
Show-Logo
Write-Section "Instalador"
Invoke-SpinnerStep "Inicializando instalador"
Ensure-Prerequisites
{install_node if runtime == "node" else install_python}
Write-Host "[+] Instalacion completada." -ForegroundColor Green
"""


def _ps_server_console_template() -> str:
    return """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Set-Location $Script:Root

function Start-ManagedServer {
  Ensure-Prerequisites
  $existing = Get-ServerPid
  if ($existing) {
    try {
      Get-Process -Id $existing -ErrorAction Stop | Out-Null
      return $existing
    } catch {
      Clear-ServerPid
    }
  }

  Invoke-SpinnerStep "Iniciando proceso servidor"
  $runner = "Set-Location '$Script:Root'; $Script:ServerCmd"
  $proc = Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-Command",$runner -PassThru -WindowStyle Hidden
  Save-ServerPid -ServerPid $proc.Id
  return $proc.Id
}

function Stop-ManagedServer {
  $serverPid = Get-ServerPid
  if (-not $serverPid) {
    Write-Host "[WARN] No hay PID guardado."
    return
  }
  try {
    Stop-Process -Id $serverPid -Force -ErrorAction Stop
    Clear-ServerPid
    Write-Host "[+] Servidor detenido (PID $serverPid)."
  } catch {
    Clear-ServerPid
    Write-Host "[WARN] PID no encontrado, se limpio el estado."
  }
}

function Show-Help {
  Write-Host ""
  Write-Host "Comandos disponibles:"
  Write-Host "  help     Mostrar ayuda"
  Write-Host "  status   Ver estado del servidor"
  Write-Host "  open     Abrir URL en navegador"
  Write-Host "  restart  Reiniciar servidor"
  Write-Host "  stop     Detener servidor"
  Write-Host "  pid      Ver PID actual"
  Write-Host "  exit     Salir de esta consola"
  Write-Host ""
}

Show-Logo
Write-Section "Consola de control del servidor"
$startedPid = Start-ManagedServer
Write-Host "[+] Servidor activo en http://localhost:$($Script:Port) (PID $startedPid)."
Show-Help

while ($true) {
  $command = (Read-Host "server").Trim().ToLowerInvariant()
  switch ($command) {
    "" { continue }
    "help" { Show-Help; continue }
    "status" { & "$PSScriptRoot\\status.ps1"; continue }
    "open" { & "$PSScriptRoot\\open.ps1"; continue }
    "restart" { Stop-ManagedServer; $startedPid = Start-ManagedServer; Write-Host "[+] Reiniciado (PID $startedPid)."; continue }
    "stop" { Stop-ManagedServer; continue }
    "pid" {
      $current = Get-ServerPid
      if ($current) { Write-Host "[INFO] PID: $current" } else { Write-Host "[WARN] Sin PID guardado." }
      continue
    }
    "exit" { break }
    default { Write-Host "[WARN] Comando no valido. Usa 'help'." }
  }
}
"""


def _ps_start_template(runtime: str) -> str:
    return f"""Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Set-Location $Script:Root
Show-Logo
Write-Section "Inicio de servidor"
Invoke-SpinnerStep "Abriendo consola de control"
$consoleScript = Join-Path $PSScriptRoot "server-console.ps1"
if (-not (Test-Path $consoleScript)) {{
  throw "No existe script de consola: $consoleScript"
}}
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File",$consoleScript | Out-Null
Write-Host "[+] Consola de control abierta."
Write-Host "[+] Comandos disponibles: help, status, open, restart, stop, exit"
"""


def _ps_stop_template() -> str:
    return """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Set-Location $Script:Root
Show-Logo
Write-Section "Detener servidor"
Invoke-SpinnerStep "Verificando PID"
$serverPid = Get-ServerPid
if (-not $serverPid) {
  Write-Host "[WARN] No hay PID guardado."
  exit 0
}
try {
  Invoke-SpinnerStep "Deteniendo proceso"
  Stop-Process -Id $serverPid -Force -ErrorAction Stop
  Clear-ServerPid
  Write-Host "[+] Servidor detenido (PID $serverPid)."
} catch {
  Clear-ServerPid
  Write-Host "[WARN] PID no encontrado, se limpio el estado."
}
"""


def _ps_status_template() -> str:
    return """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Set-Location $Script:Root
Show-Logo
Write-Section "Estado del servidor"
Invoke-SpinnerStep "Consultando estado"

$serverPid = Get-ServerPid
$running = $false
if ($serverPid) {
  try { Get-Process -Id $serverPid -ErrorAction Stop | Out-Null; $running = $true } catch { $running = $false }
}
$health = Test-Health
Write-Host "Proyecto: $($Script:Cfg.projectName)"
Write-Host "Runtime:  $($Script:Cfg.runtime)"
Write-Host "Puerto:   $($Script:Port)"
Write-Host "PID:      $serverPid"
Write-Host "Proceso:  $(if($running){'ACTIVO'} else {'INACTIVO'})"
Write-Host "Health:   $(if($health){'OK'} else {'NO RESPONDE'})"
"""


def _ps_open_template() -> str:
    return """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Show-Logo
Write-Section "Abrir servidor"
Invoke-SpinnerStep "Abriendo navegador"
Start-Process "http://localhost:$($Script:Port)/"
Write-Host "[+] Navegador abierto."
"""


def _ps_console_template() -> str:
    return """Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\\lib.ps1"
Set-Location $Script:Root

& "$PSScriptRoot\\install.ps1"
& "$PSScriptRoot\\start.ps1"

Show-Logo
Write-Host "Modo consola ServerGo"
Write-Host "Comandos: [S]tatus [O]pen [R]estart [X]stop"
Write-Host "Salida rapida: Ctrl+L"
Write-Host ""

while ($true) {
  Start-Sleep -Milliseconds 200
  if ([Console]::KeyAvailable) {
    $key = [Console]::ReadKey($true)
    if (($key.Modifiers -band [ConsoleModifiers]::Control) -and $key.Key -eq [ConsoleKey]::L) {
      & "$PSScriptRoot\\stop.ps1"
      break
    }
    switch ($key.Key) {
      "S" { & "$PSScriptRoot\\status.ps1"; Show-Logo; Write-Host "Modo consola ServerGo" }
      "O" { & "$PSScriptRoot\\open.ps1" }
      "R" { & "$PSScriptRoot\\stop.ps1"; & "$PSScriptRoot\\start.ps1" }
      "X" { & "$PSScriptRoot\\stop.ps1"; break }
      default { }
    }
  }
}
"""


def _bat_wrapper(target_ps1: str) -> str:
    return f"""@echo off
setlocal
cd /d "%~dp0\\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\\{target_ps1}"
endlocal & exit /b %ERRORLEVEL%
"""


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=True)
        file.write("\n")


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(content)
