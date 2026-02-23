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
version=0.1.2
channel=stable
release_date=2026-02-23
build=SN-F26-4
codename=Foundation
repo=https://github.com/BluePandaOpn/ServerGo
notes=Mejoras de organizacion en README/docs y menu de consola mas ordenado.
```

## Integracion en consola

- El texto de version aparece debajo del logo ASCII.
- Tambien se puede consultar por comando:
  - `run.bat version`
