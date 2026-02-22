# Sistema de Actualizacion

ServerGo integra un centro de actualizaciones via Git.

## Entrada

- Menu: `Centro de Actualizaciones`
- Comando: `run.bat update`
- Script: `scripts/update.bat`

## Operaciones

1. Ver version actual
2. Listar versiones (tags)
3. Actualizar a ultima version (`git pull --ff-only`)
4. Cambiar a version especifica (`git checkout <tag|branch>`)
5. Rollback (`git checkout -`)

## Recomendaciones

- Cierra procesos antes de cambiar version.
- Haz snapshot con `Herramientas Futuras` antes de actualizar.
- Si no hay red, la lista remota puede no estar disponible.

