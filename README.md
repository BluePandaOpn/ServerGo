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

## Regla de commits automaticos

El script genera automaticamente el prefijo:

- `SN-FYY-N`

Ejemplo:

- `SN-F26-1`

Reglas:

- `YY`: año en 2 digitos.
- `N`: version incremental por año (1, 2, 3...).
- Si pasas texto al `.bat`, se agrega despues del prefijo.
  Ejemplo: `SN-F26-2 - Ajuste de release`.

## Generar ZIP de release (recomendado)

Para evitar el limite de GitHub (100 MB por archivo), genera el paquete desde `ServerGo` usando:

- `build-release-zip.bat`

Este script:

- Lee la version desde `ServerGo/Version.sv`.
- Crea `ServerGoV<version>.zip` en `UpDate`.
- Excluye carpetas pesadas/no publicables:
  - `.tmp`
  - `.servergo`
  - `.venv`
  - `node_modules`
  - `generated-projects`
  - `certs`

Luego publica:

- `update-repo.bat "Release Vx.y.z"`
