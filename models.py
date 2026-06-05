from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class SupportedLanguage(str, Enum):
    ENGLISH = "English"
    YORUBA = "Yoruba"
    HAUSA = "Hausa"
    IGBO = "Igbo"
    PIDGIN = "Nigerian Pidgin"
    FRENCH = "French"
    SWAHILI = "Swahili"
    AMHARIC = "Amharic"
    ARABIC = "Arabic"


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    source_language: SupportedLanguage
    target_language: SupportedLanguage

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text must contain non-whitespace characters")
        return v.strip()


class TranslationResponse(BaseModel):
    source_language: str
    target_language: str
    original_text: str
    translated_text: str
    model_used: str


class TranscriptionResponse(BaseModel):
    transcribed_text: str
    language: Optional[str] = None


class SynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en")


class SynthesisResponse(BaseModel):
    audio_base64: str
    content_type: str
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict
