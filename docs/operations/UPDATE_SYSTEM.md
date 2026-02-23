# Sistema de Actualizacion

ServerGo integra un centro de actualizaciones via paquetes ZIP publicados en la rama `update`.

## Entrada

- Menu: `Centro de Actualizaciones`
- Comando: `run.bat update`
- Script: `scripts/update.bat`

## Operaciones

1. Ver version actual
2. Listar versiones (lee `origin/update` y detecta `ServerGoV*.zip`)
3. Actualizar a ultima version ZIP
4. Instalar version especifica ZIP
5. Rollback desde backup local

## Formato de versiones

- Archivo remoto: `ServerGoV0.1.3.zip`
- Nombre mostrado en menu: `ServerGo V0.1.3`

El sistema quita `.zip` y separa `ServerGo` de `Vx.y.z` automaticamente.

## Recomendaciones

- Cierra procesos antes de cambiar version.
- El instalador reemplaza la version actual (mantiene `.git`, `.servergo`, `.venv`, `.tmp`, `generated-projects`, `certs`).
- Se crea backup local en `.servergo/update-backups/` antes de instalar.
- Si no hay red, la lista remota puede no estar disponible.

