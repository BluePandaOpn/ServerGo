# Error Troubleshooting

Guia rapida para diagnosticar errores en ServerGo.

## Flujo recomendado

1. Identificar codigo (`SG-xxxx`) en consola.
2. Abrir el archivo `docs/errors/SG-xxxx.md`.
3. Revisar logs:
   - `.servergo/server.log`
   - `.servergo/api-pids/` y `.servergo/api_services.json`
4. Ejecutar diagnostico:
   - `scripts/doctor.bat`
5. Reintentar con entorno limpio (cerrar procesos activos).

## Checks por categoria

### Configuracion

- Validar `config.json`.
- Validar `Version.sv`.

### Dependencias

- `python --version`
- `node --version`
- `npm --version`
- `scripts/install.bat`

### Actualizaciones

- Confirmar `origin/update` disponible.
- Confirmar ZIP con formato `ServerGoVx.y.z.zip`.
- No incluir `.tmp`, `.servergo`, `.venv`, `node_modules` dentro del ZIP.

### Permisos

- Verificar que el proyecto no este en carpeta bloqueada.
- Ejecutar terminal con permisos adecuados si aplica.

## Referencias

- `docs/ERROR_CODES.md`
- `docs/ERROR_MAP.md`
