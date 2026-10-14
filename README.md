# api-pasword

API de generación y evaluación de contraseñas (FastAPI + uv).

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/` | Health/Hello |
| GET | `/router/generate?length=16` | Genera una contraseña (`1..256`) |
| POST | `/router/check` | Evalúa una contraseña: `{"password": "..."}` |

---

## Docker

### Build

```bash
docker build -t api-pasword:latest .
```

### Run

```bash
docker run --rm -p 8000:8000 --name api-pasword api-pasword:latest
```

### Probar

```bash
curl http://localhost:8000/
curl 'http://localhost:8000/router/generate?length=12'
curl -X POST http://localhost:8000/router/check \
  -H 'content-type: application/json' \
  -d '{"password":"Abcdef1!"}'
```

### Con Docker Compose

```bash
docker compose up -d --build   # levanta
docker compose logs -f         # logs
docker compose down            # para y borra el contenedor
```

### Estado / imágenes

```bash
docker compose ps              # estado + healthcheck
docker rmi api-pasword:latest  # borra la imagen
```

---

## Cómo está armado el `Dockerfile`

Build en dos etapas (multi-stage):

1. **`build`** — `python:3.14-slim-bookworm` + el binario oficial de `uv`.
   - `uv sync --locked --no-dev --no-install-project`: instala solo las
     dependencias (capa cacheada: cambia únicamente si tocas `uv.lock`).
   - `uv sync --locked --no-dev --no-editable`: instala el proyecto **dentro**
     del `.venv`, no como editable. Por eso en la etapa final alcanza copiar
     `.venv/`.
2. **`runtime`** — misma base, sin `uv` ni código fuente: solo el `.venv`.
   - Corre como usuario **no root** (`uid 10001`).
   - `HEALTHCHECK` contra `GET /` usando `urllib` (sin instalar `curl`).
   - `CMD uvicorn api_pasword:app --host 0.0.0.0 --port 8000 --proxy-headers`.
     El `CMD` llama a uvicorn en crudo (host/puerto fijos, sin pasar por el
     wrapper); el script `api-pasword` también existe dentro de la imagen:
     `docker exec api-pasword api-pasword --help`.

`.dockerignore` excluye `.git`, `.venv`, `__pycache__`, `dist/` y los propios
archivos de Docker. **No** ignores `README.md`: `pyproject.toml` lo referencia
(`readme = "README.md"`) y `uv_build` lo necesita para compilar.

### Comandos útiles

| Qué | Cómo |
| --- | --- |
| Variable de entorno | `docker run -e MI_VAR=valor ...` |
| Puerto distinto | `docker run -p 8080:8000 ...` |
| Shell dentro | `docker exec -it api-pasword python` |
| Logs | `docker logs -f api-pasword` |

---

## Desarrollo local (sin Docker)

```bash
uv sync
uv run api-pasword --reload          # equivalente a uvicorn api_pasword:app --reload
```

### El script `api-pasword`

`pyproject.toml` lo declara como `api-pasword = "api_pasword:main"`, y
`main()` en `src/api_pasword/__init__.py` delega en la CLI de uvicorn: usa
`UVICORN_APP` para inyectar el target por defecto (`api_pasword:app`) solo si
no pasás uno, así que **todos los flags y env vars de uvicorn valen acá**:

```bash
api-pasword                        # 127.0.0.1:8000
api-pasword --reload --port 8080
api-pasword --host 0.0.0.0
UVICORN_HOST=0.0.0.0 UVICORN_PORT=9000 api-pasword
api-pasword uvicorn:app            # target propio (le gana al default)
api-pasword --help
```

El binario vive en `.venv/bin/api-pasword`, así que con `uv run api-pasword`
(o activando el venv) siempre usás la versión actualizada del código.
