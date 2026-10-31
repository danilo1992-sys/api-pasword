from pydantic import BaseModel, ConfigDict, Field


class CheckRequest(BaseModel):
    password: str = Field(..., max_length=512)


class PhishingRequest(BaseModel):
    """Texto a analizar: se acepta ``password`` y también su nombre ``text``."""

    model_config = ConfigDict(populate_by_name=True)

    text: str = Field(
        ...,
        alias="password",
        max_length=512,
        description="Texto o contraseña a analizar (también se acepta el campo 'text').",
    )
