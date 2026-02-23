# Plugins ServerGo

Puedes usar:

- plugins simples: `plugins/*.json`
- plugins por carpeta: `plugins/<nombre>/plugin.json`

## Catalogo remoto (rama Plugins)

Desde el menu de plugins (opcion `7`) puedes abrir una interfaz PyQt6 para:

- ver catalogo de plugins de la rama `Plugins`
- seleccionar plugin visualmente
- instalar carpeta completa del plugin

Al instalar desde catalogo, ServerGo guarda archivos en:

- `plugins/<carpeta_remota>/...`

## Estructura minima del manifiesto

```json
{
  "id": "mi-plugin",
  "name": "Mi Plugin",
  "description": "Descripcion",
  "version": "1.0.0",
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

