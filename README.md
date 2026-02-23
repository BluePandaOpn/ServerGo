# Rama para las actualizaciones

## V0.1

Contenido fuente de la version:

- `ServerGoV0.1.zip`

Pasos sugeridos para publicar en `update` del repo `https://github.com/BluePandaOpn/ServerGo.git`:

1. Ir a carpeta del repo: `cd ..\ServerGo`
2. Validar rama actual: `git branch --show-current`
3. Validar cambios: `git status`
4. Agregar cambios: `git add .`
5. Crear commit: `git commit -m "Integracion ServerGo V0.1 + docs search"`
6. Subir rama: `git push origin update`

## Publicacion automatica desde UpDate

Ejecuta:

- `update-repo.bat`

Opcional con mensaje de commit:

- `update-repo.bat "Mensaje del commit"`
