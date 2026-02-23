# ServerGo Platform

Plataforma de servidor local para Windows enfocada en usuarios sin experiencia.

## Que incluye

- Entrada principal: `run.bat`
- Menu intuitivo con opciones guiadas
- Configuracion editable desde consola (`Configuraciones`)
- Servidor Node gestionado por Python (iniciar, detener, estado)
- Asistente para crear proyectos servidores nuevos en ruta personalizada
- Gestor de APIs multi-puerto (crear/iniciar/detener/estado)
- Scripts listos en `scripts/` para tareas frecuentes

## Requisitos

- Python 3.10+ en PATH
- Node.js 18+ en PATH

## Inicio rapido

1. Ejecuta `scripts\install.bat` una vez.
2. Ejecuta `run.bat`.
3. Usa el menu:
   - `1` Arranque de servidor (incluye asistente de creacion)
   - `2` Detener servidor actual
   - `3` Estado
   - `4` Configuraciones
   - `5` Tarea demo
   - `6` Gestor APIs Multi-Puerto
   - `7` Herramientas Futuras
   - `8` Sistema de Plugins
   - `9` Centro de Operaciones

## Asistente de creacion de proyecto

Desde `Arranque de servidor` puedes crear un proyecto nuevo y elegir:

- Runtime: `Node.js` o `Python`
- Si eliges Python, puedes seleccionar 5 stacks:
  - `http.server` (recomendado)
  - `Flask`
  - `FastAPI`
  - `Bottle`
  - `AioHTTP`
- Puerto del nuevo servidor
- Nombre del proyecto
- Ruta base donde generar el proyecto

El sistema crea la estructura completa con `run.bat` y `run.ps1` para arrancar el nuevo proyecto.
Ademas crea estructura organizada:

- `src/`
- `config/`
- `.servergo/`
- `public/` (opcional, para HTML/CSS/JS)
- `logs/` (opcional)
- `scripts/` con varios `.ps1` y `.bat`

## Configuracion facil desde consola

En `run.bat` entra a `Configuraciones` y puedes:

- Cambiar nombre del proyecto
- Cambiar puerto
- Activar/desactivar apertura automatica del navegador
- Ajustar velocidad de animacion
- Activar/desactivar limpiar pantalla
- Activar/desactivar pausa tras accion
- Ajustar defaults del generador (`public`, `logs`, ruta base de proyectos)
- Restaurar valores por defecto

Los cambios se guardan en `config.json`.

## Comandos directos

- `run.bat start-server`
- `run.bat stop-server`
- `run.bat status`
- `run.bat configure`
- `run.bat create-project`
- `run.bat apis`
- `run.bat future`
- `run.bat plugins`
- `run.bat https-setup`
- `run.bat ops`
- `run.bat docs-search <termino>`
- `run.bat version`
- `run.bat help`

## Gestor APIs Multi-Puerto

Permite crear microservicios API por puerto, con runtime `Node` o `Python`, y gestionarlos sin tocar codigo:

- Crear servicio API
- Creacion rapida de multiples APIs (puertos consecutivos)
- Listar servicios
- Iniciar uno o todos
- Detener uno o todos
- Eliminar servicio API de forma segura
- Ver estado y health por puerto

La configuracion del gestor se guarda en `config.json` (`apiManager`), y el catalogo en `.servergo/api_services.json`.

## Herramientas Futuras

Incluye utilidades para mantener ServerGo escalable:

- Exportar snapshot de configuracion
- Restaurar ultimo snapshot
- Limpiar estado temporal (PIDs/temporales)
- Ver/crear roadmap local en `docs/ROADMAP.md`

## Sistema de Plugins

Incluye un sistema simple para extender ServerGo con archivos JSON en `plugins/`:

- Activar/desactivar plugins
- Ejecutar plugins por ID
- Plantilla automatica para crear plugins

Acciones soportadas por plugin:

- `message`
- `command`
- `url`

## Documentacion Completa

Se agrego carpeta `docs/` con documentacion avanzada:

- `docs/README.md`
- `docs/USER_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIG.md`
- `docs/INSTALL.md`
- `docs/UPDATE_SYSTEM.md`
- `docs/ERROR_CODES.md`
- `docs/DOCKER.md`
- `docs/PLUGINS.md`
- `docs/LICENSE-APPENDIX.md`
- Busqueda local de documentacion:
  - `run.bat docs-search <termino>`
  - `scripts\docs-search.bat <termino>`

## HTTPS Facil

ServerGo incluye conversion simple de HTTP a HTTPS para entorno local:

- Activar desde `Configuraciones` (opciones HTTPS)
- O en un paso con:
  - `run.bat https-setup`
  - `scripts\https-setup.bat`

Cuando HTTPS esta activo:

- Se sirve en `https://localhost:<defaultPort>`
- Puede generar certificado local automaticamente (`https.autoGenerateCert`)
- Puede redirigir HTTP a HTTPS (`https.redirectHttp`, `https.httpPort`)

## Centro de Operaciones

Panel rapido para tareas globales:

- Arranque total (servidor principal + APIs + plugins)
- Parada total
- Diagnostico total
- Alternar automatizaciones
- Generar reporte operativo JSON en `.servergo/reports/`

Automatizaciones disponibles en configuracion:

- `automation.startAllApisWithMainServer`
- `automation.runEnabledPluginsOnStart`

## Centro de Actualizaciones

- Menu dedicado para versionado y cambio de releases.
- Soporta:
  - version actual (programa + estado de instalacion)
  - listado de paquetes en rama `update` (`ServerGoV*.zip`)
  - instalar ultima version disponible
  - instalar version especifica
  - rollback desde backup local

Accesos:

- `run.bat update`
- `scripts/update.bat`

## Metadata de Version

ServerGo incluye archivo `Version.sv` en la raiz con metadatos:

- version
- channel
- release_date
- build
- codename
- repo
- notes

Se muestra debajo del logo en consola y tambien por comando:

- `run.bat version`

## Sistema de Errores

ServerGo ahora incluye codigos de error (`SG-xxxx`) y referencia a docs.
Configura tu repositorio en `support.repoUrl` para enlazar errores a tu repo.
Ejemplo:

- `support.repoUrl = "https://github.com/TU_USUARIO/TU_REPO"`

## Scripts de administracion

Cada `.bat` llama su `.ps1` equivalente:

- `scripts\install.bat` / `scripts\install.ps1`
- `scripts\start-server.bat` / `scripts\start-server.ps1`
- `scripts\stop-server.bat` / `scripts\stop-server.ps1`
- `scripts\status.bat` / `scripts\status.ps1`
- `scripts\configure.bat` / `scripts\configure.ps1`
- `scripts\doctor.bat` / `scripts\doctor.ps1`
- `scripts\create-project.bat` / `scripts\create-project.ps1`
- `scripts\https-setup.bat` / `scripts\https-setup.ps1`
- `scripts\docs-search.bat` / `scripts\docs-search.ps1`

Los proyectos generados incluyen tambien:

- `scripts\install.bat` / `scripts\install.ps1`
- `scripts\start.bat` / `scripts\start.ps1`
- `scripts\stop.bat` / `scripts\stop.ps1`
- `scripts\status.bat` / `scripts\status.ps1`
- `scripts\open.bat` / `scripts\open.ps1`
- `scripts\console.bat` / `scripts\console.ps1` (salir con `Ctrl+L`)

## Endpoints

- `http://localhost:3000/`
- `http://localhost:3000/api/health`
- `http://localhost:3000/api/hello`

## Estructura

```text
.
|- run.bat
|- config.json
|- python/
|  |- main.py
|  |- cli.py
|  |- ui.py
|  `- utils.py
|- node/
|  |- package.json
|  |- server.js
|  |- routes/example.js
|  `- public/index.html
`- scripts/
   |- *.bat
   `- *.ps1
```
