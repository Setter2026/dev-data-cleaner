from typing import Literal

from pydantic import BaseModel, Field


class DTO(BaseModel):
    # Mandatory field (raises ValidationError if missing or invalid type)
    id: int

    # Optional fields (validated strictly if present; defaults to None if missing)
    name: str | None = Field(default=None, min_length=1)
    age: int | None = Field(default=None, gt=0, lt=120)
    status: Literal["Active", "Pending"] | None = Field(default=None)