import re
import secrets
import string

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/router")

NIVELES = {
    5: "Muy fuerte",
    4: "Fuerte",
    3: "Moderada",
    2: "Debil",
    1: "Muy debil",
    0: "Inaceptable",
}


class CheckRequest(BaseModel):
    password: str = Field(..., max_length=512)


@router.get("/generate")
def generate(length: int = Query(default=16, ge=1, le=256)):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(caracteres) for _ in range(length))
    return password


@router.post("/check")
def check(body: CheckRequest):
    password = body.password

    detalles = {
        "longitud_minima": len(password) >= 8,
        "mayuscula": bool(re.search(r"[A-Z]", password)),
        "minuscula": bool(re.search(r"[a-z]", password)),
        "numero": bool(re.search(r"\d", password)),
        "especial": any(c in string.punctuation for c in password),
    }
    points = sum(detalles.values())

    return {
        "nivel": NIVELES.get(points, "Inaceptable"),
        "punctuation": points,
        "detalles": detalles,
    }
