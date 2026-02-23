# Error Codes

Catalogo completo de errores de ServerGo.

Cada codigo tiene su archivo dedicado en `docs/errors/`.

## Errores activos del runtime

- `SG-0001` Configuracion invalida
- `SG-0002` Dependencia faltante
- `SG-0003` Operacion de red fallida
- `SG-0004` Operacion Git/Update fallida
- `SG-0005` Operacion de plugin fallida
- `SG-9999` Error no controlado

## Errores documentados para expansion

- `SG-0100` Fallo de arranque principal
- `SG-0101` Puerto en uso
- `SG-0102` Estado/PID inconsistente
- `SG-0200` Configuracion corrupta
- `SG-0201` Metadata de version invalida (`Version.sv`)
- `SG-0300` Dependencias Node incompletas
- `SG-0301` Dependencias Python incompletas
- `SG-0400` Paquete de actualizacion invalido
- `SG-0401` Integridad de actualizacion fallida
- `SG-0500` API Manager fallo de operacion
- `SG-0501` API Manager conflicto de puertos
- `SG-0600` Plugin con esquema invalido
- `SG-0700` HTTPS/Certificado invalido
- `SG-0800` Permisos insuficientes en filesystem
- `SG-0900` Recursos insuficientes (rendimiento/memoria)

## Rutas de soporte

- Mapa: `docs/errors/ERROR_MAP.md`
- Guia de diagnostico: `docs/errors/ERROR_TROUBLESHOOTING.md`

