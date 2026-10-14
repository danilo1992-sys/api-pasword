# syntax=docker/dockerfile:1

########################################################################
# build stage — instala las dependencias con uv sobre el lockfile
########################################################################
FROM python:3.14-slim-bookworm AS build

# uv binario oficial (imagen de Astral), sin shell ni libc extra
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# UV_COMPILE_BYTECODE: precompila los .pyc -> arranque mas rapido
# UV_PYTHON_DOWNLOADS=never: usa el python de la imagen base, no descarga otro
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Capa 1: dependencias. Se cachea mientras no cambien pyproject/uv.lock.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

# Capa 2: el codigo. --no-editable instala el paquete en el venv de verdad,
# asi en la imagen final solo hace falta copiar .venv/.
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

########################################################################
# runtime stage — solo python + el venv ya resuelto
########################################################################
FROM python:3.14-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# usuario sin privilegios
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=build /app/.venv /app/.venv

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2).status == 200 else 1)"

# --proxy-headers: respeta X-Forwarded-* si hay un reverse proxy delante
CMD ["uvicorn", "api_pasword:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
