import os

from fastapi import FastAPI
from .routes.routes import router as password

app = FastAPI()

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
