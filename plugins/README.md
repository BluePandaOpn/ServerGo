# Plugins ServerGo

Coloca aqui archivos `*.json` para extender ServerGo sin tocar codigo.

## Estructura minima

```json
{
  "id": "mi-plugin",
  "name": "Mi Plugin",
  "description": "Descripcion",
  "actions": [
    {"type": "message", "text": "Hola"},
    {"type": "command", "command": "cmd /c run.bat status"},
    {"type": "url", "url": "http://localhost:3000/api/health"}
  ]
}
```

## Tipos de accion soportados

- `message`
- `command`
- `url`

