# Error Codes

Este catalogo permite mapear errores del programa a acciones concretas.

## sg-0001

- Titulo: Configuracion invalida
- Accion: revisar `config.json` y `docs/CONFIG.md`

## sg-0002

- Titulo: Dependencia faltante
- Accion: ejecutar `scripts/install.bat`

## sg-0003

- Titulo: Operacion de red fallida
- Accion: revisar conectividad/proxy/firewall

## sg-0004

- Titulo: Operacion Git fallida
- Accion: revisar `docs/UPDATE_SYSTEM.md`

## sg-0005

- Titulo: Operacion de plugin fallida
- Accion: revisar `plugins/*.json` y `docs/PLUGINS.md`

## sg-9999

- Titulo: Error no controlado
- Accion: revisar `.servergo/server.log` y reportar con contexto

