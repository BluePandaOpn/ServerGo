# Guia de Usuario (ServerGo)

Esta guia explica como usar ServerGo paso a paso.

## 1. Arranque rapido

1. Ejecuta `scripts/install.bat`
2. Ejecuta `run.bat`
3. En el menu principal usa:
- `1` Servidores y despliegue
- `2` Plataforma y extensiones
- `3` Sistema y mantenimiento

## 2. Menu principal (3 opciones)

- **1. Servidores y despliegue**:
  - arranque y creacion de proyecto
  - detener/reiniciar servidor principal
  - ver ultimas lineas del log principal
  - diagnostico avanzado de servidor
  - acceso directo al gestor APIs

- **2. Plataforma y extensiones**:
  - configuraciones
  - plugins
  - herramientas futuras
  - centro de operaciones

- **3. Sistema y mantenimiento**:
  - actualizaciones
  - busqueda en docs
  - version instalada
  - estado completo servidor + APIs
  - centro PowerShell avanzado (PS1)

## 3. Modulos disponibles

- **Arranque de servidor**:
  - iniciar servidor local
  - crear proyecto nuevo (Node/Python)

- **Gestor APIs Multi-Puerto**:
  - crear, iniciar, detener, listar APIs
  - creacion rapida masiva

- **Sistema de Plugins**:
  - activar/desactivar plugins
  - ejecutar plugin por ID
  - instalar plugins desde catalogo visual (PyQt6)

- **Centro de Operaciones**:
  - arranque/parada total
  - diagnostico total
  - reporte operativo

- **Centro de Actualizaciones**:
  - ver version
  - listar versiones ZIP de rama `update`
  - instalar ultima version o una version especifica
  - rollback desde backup local

- **Version del programa**:
  - se muestra debajo del logo en consola
  - comando rapido: `run.bat version`

## 4. HTTPS

Opciones:

- `run.bat https-setup`
- o configurar desde menu `Configuraciones`

Cuando HTTPS esta activo:
- URL principal: `https://localhost:<puerto>`
- opcional: redirect desde HTTP

## 5. Sistema de errores y codigos

Cuando ocurre un error, ServerGo muestra:

- codigo de error (ej. `SG-0004`)
- descripcion resumida
- sugerencia de accion
- URL al repositorio para leer docs del error

Ejemplo:

`[SG-0004] ... | Referencia: https://github.com/BluePandaOpn/ServerGo/blob/main/docs/errors/ERROR_CODES.md#sg-0004`

## 6. Configurar URL real del repositorio

En `config.json`:

```json
"support": {
  "repoUrl": "https://github.com/BluePandaOpn/ServerGo"
}
```

Tambien puedes hacerlo desde `Configuraciones` (opcion de URL de repositorio).

## 7. Donde revisar logs y estado

- servidor principal: `.servergo/server.log`
- catalogo APIs: `.servergo/api_services.json`
- reportes operativos: `.servergo/reports/`

## 8. Centro PS1 avanzado

Puedes abrirlo con:

- `run.bat ps-console`
- `scripts\ps-console.bat`

Funciones destacadas:

- dashboard animado en consola
- start/stop/restart del servidor principal
- estado general y acceso a APIs/plugins/update
- tail de log principal
- terminal PowerShell interactiva con atajos:
  - `sg-start`
  - `sg-stop`
  - `sg-status`
  - `sg-apis`
  - `sg-plugins`
  - `sg-update`
  - `sg-docs <termino>`

