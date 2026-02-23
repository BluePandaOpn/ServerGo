# Contributing to ServerGo

Gracias por contribuir.

## Flujo recomendado

1. Crea un issue (bug, feature o docs).
2. Crea una rama corta desde `main`.
3. Haz cambios pequeños y enfocados.
4. Valida localmente:
   - `run.bat status`
   - `python -m py_compile python\\main.py python\\cli.py`
5. Actualiza docs cuando cambie comportamiento.
6. Abre Pull Request con contexto y pruebas.

## Estandar de cambios

- Mantener compatibilidad de comandos existentes.
- Incluir manejo de errores (`SG-xxxx`) cuando aplique.
- Evitar rutas hardcodeadas fuera de la raiz del proyecto.

## Convencion de commits sugerida

- `feat: ...`
- `fix: ...`
- `docs: ...`
- `chore: ...`
