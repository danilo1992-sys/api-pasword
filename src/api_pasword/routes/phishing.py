import unicodedata

from fastapi import APIRouter

from ..models.model import PhishingRequest

pishing = APIRouter(prefix="/phishing")


def _analizar(texto: str) -> list[dict]:
    """Lista los caracteres no ASCII del texto (homógrafos, invisibles...)."""
    sospechosos: list[dict] = []

    for posicion, caracter in enumerate(texto, start=1):
        if caracter.isascii() and caracter.isprintable():
            continue

        nombre = unicodedata.name(caracter, "Desconocido")
        categoria = unicodedata.category(caracter)

        # Letras latinas con tilde/ñ (á, é, ï...): normales en español.
        riesgo = "bajo" if categoria.startswith("L") and "LATIN" in nombre else "alto"

        sospechosos.append(
            {
                "posicion": posicion,
                "caracter": caracter,
                "nombre": nombre,
                "categoria": categoria,
                "riesgo": riesgo,
            }
        )

    return sospechosos


@pishing.post("/check")
def check(body: PhishingRequest) -> dict:
    detalles = _analizar(body.text)

    if any(detalle["riesgo"] == "alto" for detalle in detalles):
        nivel = "Sospechoso"
    elif detalles:
        nivel = "Revisar"
    else:
        nivel = "Seguro"

    return {
        "nivel": nivel,
        "sospechosos": len(detalles),
        "total": len(body.text),
        "detalles": detalles,
    }
