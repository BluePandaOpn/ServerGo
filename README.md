# ServerGo Platform

Plataforma local para administrar servidores, APIs, plugins y operaciones desde una sola consola en Windows.

## Inicio rapido

1. Ejecuta `scripts\install.bat`
2. Ejecuta `run.bat`
3. Usa el menu principal para iniciar servidor, revisar estado o configurar el sistema

## Navegacion rapida

- Documentacion central: `docs/README.md`
- Guia de uso: `docs/USER_GUIDE.md`
- Instalacion: `docs/INSTALL.md`
- Configuracion: `docs/CONFIG.md`
- Arquitectura: `docs/ARCHITECTURE.md`
- Docker: `docs/DOCKER.md`

## Modos principales

| Opcion | Modulo | Uso |
|---|---|---|
| `1` | Arranque de servidor | Inicia servidor o crea proyecto nuevo |
| `3` | Estado | Verifica entorno, PID, puerto y salud |
| `4` | Configuraciones | Ajusta puertos, UI, scaffold, HTTPS y automatizaciones |
| `6` | API Manager | Gestion multi-puerto de APIs Node/Python |
| `8` | Plugins | Activar, desactivar y ejecutar plugins JSON |
| `9` | Operaciones | Arranque/parada total y reporte operativo |
| `10` | Actualizaciones | Listar ZIPs, actualizar y rollback |

## Comandos directos

- `run.bat start-server`
- `run.bat stop-server`
- `run.bat status`
- `run.bat configure`
- `run.bat create-project`
- `run.bat apis`
- `run.bat future`
- `run.bat plugins`
- `run.bat ops`
- `run.bat update`
- `run.bat https-setup`
- `run.bat docs-search <termino>`
- `run.bat version`
- `run.bat help`

## Estructura del repositorio

```text
ServerGo/
|- run.bat
|- config.json
|- Version.sv
|- python/          # CLI principal y logica de orquestacion
|- scripts/         # wrappers .bat/.ps1 para tareas comunes
|- docs/            # documentacion tecnica y de usuario
|- plugins/         # plugins JSON (extensiones de comportamiento)
`- node/            # servidor base Node.js
```

## Requisitos

- Python 3.10+
- Node.js 18+
- npm en `PATH`

## Version y metadata

`Version.sv` incluye:

- `version`
- `channel`
- `release_date`
- `build`
- `codename`
- `repo`
- `notes`

Consulta rapida por consola:

- `run.bat version`

## Documentacion extendida

Consulta `docs/README.md` para el indice completo de:

- arquitectura
- instalacion
- configuracion
- plugins
- errores (`SG-xxxx`)
- actualizaciones y release management
