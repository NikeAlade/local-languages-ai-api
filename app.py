import os
import base64
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from models import (
    TranslationRequest, TranslationResponse,
    TranscriptionResponse, SynthesisRequest, SynthesisResponse,
    HealthResponse, SupportedLanguage,
)
from services import GroqTranslationService, SpitchAudioService, VOICE_MAP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("local-languages-api")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SPITCH_API_KEY = os.environ.get("SPITCH_API_KEY", "")

translation_service = GroqTranslationService(GROQ_API_KEY)
audio_service = SpitchAudioService(SPITCH_API_KEY)

app = FastAPI(
    title="Local Languages AI API",
    description="Multilingual API for translation, speech recognition, and text-to-speech.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services={
            "groq": "configured" if GROQ_API_KEY else "missing key",
            "spitch": "configured" if SPITCH_API_KEY else "missing key",
        },
    )


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    if request.source_language == request.target_language:
        raise HTTPException(status_code=400, detail="Source and target languages must be different.")
    translated = translation_service.translate(
        text=request.text,
        source_lang=request.source_language.value,
        target_lang=request.target_language.value,
    )
    return TranslationResponse(
        source_language=request.source_language.value,
        target_language=request.target_language.value,
        original_text=request.text,
        translated_text=translated,
        model_used=translation_service.model,
    )


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
):
    allowed_types = {"audio/wav", "audio/mpeg", "audio/ogg", "audio/flac", "audio/x-wav", "audio/mp3"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {file.content_type}")
    audio_bytes = await file.read()
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 25 MB limit.")
    result = audio_service.transcribe(audio_bytes, language)
    return TranscriptionResponse(transcribed_text=result["transcribed_text"], language=language)


@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesisRequest):
    voice = VOICE_MAP.get(request.language, "sade")
    audio_bytes = audio_service.synthesize(request.text, request.language, voice)
    return SynthesisResponse(
        audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
        content_type="audio/wav",
        message="Speech synthesized successfully",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})
