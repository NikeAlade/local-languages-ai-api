import io
import logging
from fastapi import HTTPException
from groq import Groq
from spitch import Spitch

logger = logging.getLogger("local-languages-api")

VOICE_MAP = {
    "en": "amina",
    "yo": "sade",
    "ha": "amina",
    "ig": "amina",
    "pcm": "amina",
    "fr": "amina",
    "sw": "amina",
    "am": "amina",
    "ar": "amina",
}


class GroqTranslationService:

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        system_prompt = (
            f"You are a professional translator fluent in {source_lang} and {target_lang}. "
            f"Translate the following text from {source_lang} to {target_lang}.\n\n"
            f"Rules:\n"
            f"- Output ONLY the translation, nothing else.\n"
            f"- Do NOT transliterate — use actual {target_lang} words and grammar.\n"
            f"- Preserve tone, meaning, and cultural context.\n"
            f"- Use proper diacritics/tone marks where required."
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.2,
                max_tokens=2048,
            )
            translated = response.choices[0].message.content.strip()
            if translated.startswith('"') and translated.endswith('"'):
                translated = translated[1:-1]
            return translated
        except Exception as e:
            logger.error(f"Groq translation error: {e}")
            raise HTTPException(status_code=502, detail=f"Translation service error: {str(e)}")


class SpitchAudioService:

    def __init__(self, api_key: str):
        self.client = Spitch(api_key=api_key)

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> dict:
        try:
            response = self.client.speech.transcribe(language=language, content=audio_bytes)
            return {"transcribed_text": response.text, "language": language}
        except Exception as e:
            logger.error(f"Spitch ASR error: {e}")
            raise HTTPException(status_code=502, detail=f"ASR service error: {str(e)}")

    def synthesize(self, text: str, language: str = "en", voice: str = "sade") -> bytes:
        try:
            response = self.client.speech.generate(text=text, language=language, voice=voice)
            if isinstance(response, bytes):
                return response
            if hasattr(response, "read"):
                return response.read()
            if hasattr(response, "content"):
                return response.content
            return bytes(response)
        except Exception as e:
            logger.warning(f"Spitch TTS unavailable, falling back to gTTS: {e}")

        try:
            from gtts import gTTS
            gtts_lang = language if language != "pcm" else "en"
            tts = gTTS(text=text, lang=gtts_lang)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            logger.error(f"gTTS fallback also failed: {e}")
            raise HTTPException(status_code=502, detail=f"TTS service error: {str(e)}")
