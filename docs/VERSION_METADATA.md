# Version Metadata

ServerGo usa `Version.sv` en la raiz del proyecto para metadatos de version.

## Campos soportados

- `version`
- `channel`
- `release_date`
- `build`
- `codename`
- `repo`
- `notes`

## Ejemplo

```text
version=0.1.1
channel=stable
release_date=2026-02-23
build=SN-F26-2
codename=Foundation
repo=https://github.com/BluePandaOpn/ServerGo
notes=Base estable con sistema de actualizacion ZIP.
```

## Integracion en consola

- El texto de version aparece debajo del logo ASCII.
- Tambien se puede consultar por comando:
  - `run.bat version`
