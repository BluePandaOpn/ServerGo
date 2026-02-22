# Configuracion

Archivo principal: `config.json`

## Claves

- `projectName`
- `defaultPort`
- `autoOpenBrowser`
- `ui.clearScreenOnMenu`
- `ui.pauseAfterAction`
- `scaffold.*`
- `apiManager.*`
- `future.*`
- `plugins.enabled`
- `plugins.defaultTimeoutSec`
- `https.enabled`
- `https.autoGenerateCert`
- `https.keyPath`
- `https.certPath`
- `https.redirectHttp`
- `https.httpPort`
- `automation.startAllApisWithMainServer`
- `automation.runEnabledPluginsOnStart`
- `support.repoUrl`

## Ejemplo minimo

```json
{
  "projectName": "ServerGo",
  "defaultPort": 3000,
  "https": {
    "enabled": false
  }
}
```

