# Guia de Usuario (ServerGo)

Esta guia explica como usar ServerGo paso a paso.

## 1. Arranque rapido

1. Ejecuta `scripts/install.bat`
2. Ejecuta `run.bat`
3. En el menu principal usa:
- `1` Arranque de servidor
- `3` Estado del entorno
- `4` Configuraciones

## 2. Menus principales

- **Arranque de servidor**:
  - iniciar servidor local
  - crear proyecto nuevo (Node/Python)

- **Gestor APIs Multi-Puerto**:
  - crear, iniciar, detener, listar APIs
  - creacion rapida masiva

- **Sistema de Plugins**:
  - activar/desactivar plugins
  - ejecutar plugin por ID

- **Centro de Operaciones**:
  - arranque/parada total
  - diagnostico total
  - reporte operativo

- **Centro de Actualizaciones**:
  - ver version
  - listar versiones ZIP de rama `update`
  - instalar ultima version o una version especifica
  - rollback desde backup local

## 3. HTTPS

Opciones:

- `run.bat https-setup`
- o configurar desde menu `Configuraciones`

Cuando HTTPS esta activo:
- URL principal: `https://localhost:<puerto>`
- opcional: redirect desde HTTP

## 4. Sistema de errores y codigos

Cuando ocurre un error, ServerGo muestra:

- codigo de error (ej. `SG-0004`)
- descripcion resumida
- sugerencia de accion
- URL al repositorio para leer docs del error

Ejemplo:

`[SG-0004] ... | Referencia: https://github.com/BluePandaOpn/ServerGo/blob/main/docs/ERROR_CODES.md#sg-0004`

## 5. Configurar URL real del repositorio

En `config.json`:

```json
"support": {
  "repoUrl": "https://github.com/BluePandaOpn/ServerGo"
}
```

Tambien puedes hacerlo desde `Configuraciones` (opcion de URL de repositorio).

## 6. Donde revisar logs y estado

- servidor principal: `.servergo/server.log`
- catalogo APIs: `.servergo/api_services.json`
- reportes operativos: `.servergo/reports/`

