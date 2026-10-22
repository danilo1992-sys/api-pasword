import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.routes import router as password

app = FastAPI()

# Origenes permitidos: dev/preview locales y los despliegues en Render
# (el front está en https://frontend-password.onrender.com).
FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "https://frontend-password.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(password)

@app.get("/")
def home():
    return {"mesages": "Hello World"}


def main() -> None:
    """Entry point of the ``api-pasword`` console script.

    It delegates to uvicorn's CLI, so every uvicorn flag and env var also
    works here: ``api-pasword --reload``, ``api-pasword --port 8080``,
    ``UVICORN_HOST=0.0.0.0 api-pasword``...

    ``UVICORN_APP`` only supplies the target when none is passed on the
    command line, so ``api-pasword uvicorn:app`` still wins over it.
    """
    os.environ.setdefault("UVICORN_APP", "api_pasword:app")

    from uvicorn.main import main as uvicorn_cli

    uvicorn_cli()
