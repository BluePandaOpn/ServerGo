# ServerGo Platform

Plataforma local para administrar servidores, APIs, plugins, operaciones y herramientas PS1 desde una sola consola.

## Inicio rapido

1. Ejecuta `scripts\install.bat`
2. Ejecuta `run.bat`
3. Usa el menu principal:
   - `1` Servidores y despliegue
   - `2` Plataforma y extensiones
   - `3` Sistema y mantenimiento

## Documentacion central

- Indice completo: `docs/README.md`
- Instalacion: `docs/getting-started/INSTALL.md`
- Guia de usuario: `docs/getting-started/USER_GUIDE.md`
- Arquitectura: `docs/architecture/ARCHITECTURE.md`
- Configuracion: `docs/configuration/CONFIG.md`
- Operaciones: `docs/operations/PROJECT_MANAGEMENT.md`
- Plugins: `docs/plugins/PLUGINS.md`
- Errores: `docs/errors/ERROR_CODES.md`

## Busqueda de documentacion

Comandos:

- `run.bat docs-search <termino>`
- `scripts\docs-search.bat <termino>`

La busqueda recorre toda la documentacion (`docs/**/*.md`), incluyendo subcarpetas.

## Comandos directos

- `run.bat start-server`
- `run.bat stop-server`
- `run.bat status`
- `run.bat configure`
- `run.bat create-project`
- `run.bat apis`
- `run.bat plugins`
- `run.bat ops`
- `run.bat update`
- `run.bat ps-console`
- `run.bat https-setup`
- `run.bat docs-search <termino>`
- `run.bat version`
- `run.bat help`

## Estructura del proyecto

```text
ServerGo/
|- run.bat
|- config.json
|- Version.sv
|- python/          # orquestacion y CLI
|- scripts/         # herramientas .ps1/.bat
|- docs/            # documentacion organizada por dominios
|- plugins/         # plugins locales y catalogo instalado
|- node/            # servidor base
`- .servergo/       # estado runtime (pids, reportes, backups)
```

## Requisitos

- Python 3.10+
- Node.js 18+
- npm en `PATH`

## Comunidad y gobernanza

Archivos para uso en GitHub:

- Licencia: `LICENSE`
- Guia de contribucion: `CONTRIBUTING.md`
- Codigo de conducta: `CODE_OF_CONDUCT.md`
- Seguridad: `SECURITY.md`
- Soporte: `SUPPORT.md`
- Plantillas de issues/PR: `.github/`
