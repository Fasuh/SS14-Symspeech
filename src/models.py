from pydantic import BaseModel, Field, field_validator
from src.config import get_config

_max_text = get_config()["max_text_length"]

class TtsRequest(BaseModel):
    id: str
    t: str

    r: str
    pitch: int = Field(default=0, ge=-24, le=24)
    speed: float = Field(default=0.44, ge=0.1, le=1.0)
    pause: float = Field(default=0.36, ge=0.05, le=1.0)
    poly: int = Field(default=1, ge=1, le=8)
    scale: int = Field(default=0, ge=0, le=6)
    vol: float = Field(default=1.0, ge=0.1, le=2.0)
    emotion: int = Field(default=0, ge=0, le=5)
    e: int = Field(default=0, ge=0, le=6)
    ts: int = 0

    @field_validator("t")
    @classmethod
    def truncate_text(cls, v: str) -> str:
        return v[:_max_text]