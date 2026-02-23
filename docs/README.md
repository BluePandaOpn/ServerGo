# ServerGo Docs

Indice oficial de documentacion del proyecto.

Repositorio: https://github.com/BluePandaOpn/ServerGo

## Estructura de docs

```text
docs/
|- README.md
|- getting-started/
|- architecture/
|- configuration/
|- operations/
|- plugins/
|- errors/
`- legal/
```

## Ruta recomendada (primera vez)

1. `getting-started/INSTALL.md`
2. `getting-started/USER_GUIDE.md`
3. `configuration/CONFIG.md`
4. `architecture/ARCHITECTURE.md`

## Documentos por categoria

### Uso e instalacion

- [INSTALL.md](getting-started/INSTALL.md) - instalacion y primer arranque
- [USER_GUIDE.md](getting-started/USER_GUIDE.md) - uso diario de menus y comandos

### Arquitectura y configuracion

- [ARCHITECTURE.md](architecture/ARCHITECTURE.md) - arquitectura general
- [CONFIG.md](configuration/CONFIG.md) - configuracion completa (`config.json`)

### Operaciones y despliegue

- [DOCKER.md](operations/DOCKER.md) - Docker/Docker Compose
- [UPDATE_SYSTEM.md](operations/UPDATE_SYSTEM.md) - actualizaciones ZIP
- [VERSION_METADATA.md](operations/VERSION_METADATA.md) - metadata de `Version.sv`
- [PROJECT_MANAGEMENT.md](operations/PROJECT_MANAGEMENT.md) - gestion operativa y release flow

### Plugins

- [PLUGINS.md](plugins/PLUGINS.md) - arquitectura de plugins y catalogo visual

### Errores y diagnostico

- [ERROR_CODES.md](errors/ERROR_CODES.md) - catalogo `SG-xxxx`
- [ERROR_MAP.md](errors/ERROR_MAP.md) - mapa de enlaces por codigo
- [ERROR_TROUBLESHOOTING.md](errors/ERROR_TROUBLESHOOTING.md) - guia de diagnostico
- [errors/](errors/) - detalle por codigo (`SG-0001.md`, etc.)

### Legal

- [LICENSE-APPENDIX.md](legal/LICENSE-APPENDIX.md) - notas legales y apendice

## Busqueda local de documentacion

Desde la raiz:

- `run.bat docs-search <termino>`
- `scripts\docs-search.bat <termino>`

La busqueda recorre `docs/**/*.md`.
