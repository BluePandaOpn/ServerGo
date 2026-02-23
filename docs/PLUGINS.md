# Plugins

Los plugins viven en `plugins/*.json`.

## Formato

```json
{
  "id": "mi-plugin",
  "name": "Mi Plugin",
  "actions": [
    {"type": "message", "text": "Hola"},
    {"type": "command", "command": "cmd /c run.bat status"},
    {"type": "url", "url": "http://localhost:3000/api/health"}
  ]
}
```

## Seguridad

- Solo usa comandos de confianza.
- Revisa `cwd` y `timeoutSec` en acciones `command`.
- Activa plugins manualmente desde el menu antes de ejecutarlos.

