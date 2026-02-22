# Project Management

Guia de gestion para evolucionar ServerGo.

## Flujo recomendado

1. Crear issue (feature/bug)
2. Definir impacto y riesgo
3. Implementar en rama corta
4. Validar scripts + menus + docs
5. Publicar release/tag
6. Actualizar `docs/UPDATE_SYSTEM.md`

## Convencion de versiones

- `vMAJOR.MINOR.PATCH`
- `MAJOR`: cambios incompatibles
- `MINOR`: nuevas funciones compatibles
- `PATCH`: fixes sin romper contratos

## Checklist de release

- tests y validaciones locales
- update de docs
- update de error codes si aplica
- tag Git publicado
- verificacion del centro de actualizaciones

## Incident Response

- capturar codigo de error `SG-xxxx`
- revisar `.servergo/server.log`
- revisar `docs/ERROR_CODES.md`
- generar reporte desde Centro de Operaciones

