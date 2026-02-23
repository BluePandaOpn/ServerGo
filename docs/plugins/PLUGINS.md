# Plugins

ServerGo soporta dos formatos:

- `plugins/*.json` (plugin simple)
- `plugins/<carpeta>/plugin.json` (plugin empaquetado por carpeta)

## Instalador visual (PyQt6)

En `Sistema de Plugins`:

- opcion `7` abre el catalogo visual (PyQt6)
- la UI consulta la rama remota `Plugins` (o `plugins`) del mismo repositorio
- solo muestra carpetas que incluyan `plugin.json` o `manifest.json`
- al seleccionar e instalar:
  - se cierra la ventana
  - continua en consola
  - se descarga la carpeta completa del plugin a `plugins/<carpeta>/`
  - se activa el plugin automaticamente

Si PyQt6 no esta instalado, ServerGo muestra instruccion para instalarlo en `.venv`.

## Formato minimo de manifiesto

```json
{
  "id": "mi-plugin",
  "name": "Mi Plugin",
  "description": "Descripcion del plugin",
  "version": "1.0.0",
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

