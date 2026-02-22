# Docker

ServerGo incluye soporte basico Docker.

## Build

```bash
docker build -t servergo:local .
```

## Run

```bash
docker run --rm -p 3000:3000 -p 8080:8080 servergo:local
```

## Docker Compose

```bash
docker compose up --build
```

## Notas

- Si HTTPS esta activo y usa cert local, monta `certs/` segun necesidad.
- En desarrollo puedes ajustar `config.json` antes de levantar contenedor.

