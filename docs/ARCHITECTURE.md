# Arquitectura

ServerGo es una plataforma local de administracion de servidores con capas:

1. `run.bat`:
- entrada principal para usuarios Windows.

2. Core Python (`python/*.py`):
- menus, orquestacion, configuracion, operaciones y actualizaciones.

3. Servidor Node (`node/`):
- servicio HTTP/HTTPS principal.

4. Scripts PowerShell (`scripts/*.ps1` + wrappers `.bat`):
- operaciones guiadas para usuarios no tecnicos.

5. Estado runtime (`.servergo/`):
- pids, logs, catalogos de APIs y reportes.

## Modulos principales

- `python/cli.py`: menu principal y operaciones base.
- `python/api_manager.py`: APIs multi-puerto.
- `python/plugin_system.py`: plugins JSON.
- `python/update_manager.py`: actualizaciones/versionado via Git.
- `python/future_tools.py`: snapshots/roadmap/limpieza.
- `python/error_system.py`: errores con codigo y referencia.

