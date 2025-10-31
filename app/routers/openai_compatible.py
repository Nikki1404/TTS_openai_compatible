# app/routers/openai_compatible.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional

from app.core.config import settings
from app.tts.kokoro_engine import synthesize_np, encode_audio, maybe_save

router = APIRouter(prefix="/v1")

class AudioSpeechIn(BaseModel):
    # OpenAI-compatible body
    model: str = Field("tts-1", description="Ignored; kept for compatibility")
    voice: Optional[str] = Field(None, description="Kokoro voice id (e.g., af_heart)")
    input: str = Field(..., description="Text to synthesize")
    response_format: Optional[str] = Field("wav", description="wav|mp3|ogg|flac")
    speed: Optional[float] = Field(None, description="1.0 = normal")
    stream: Optional[bool] = Field(False, description="If true, would stream (not implemented; returns full)")
    lang_code: Optional[str] = Field(None, description="Kokoro language code (default from server)")
    sample_rate: Optional[int] = Field(None, description="Default from server")
    save: Optional[bool] = Field(None, description="Override server save_audio")

@router.post("/audio/speech")
async def audio_speech(body: AudioSpeechIn):
    # Validate format
    fmt = (body.response_format or "wav").lower()
    if fmt not in settings.allowed_formats and fmt != "wav":
        raise HTTPException(status_code=400, detail=f"Unsupported response_format='{fmt}'")

    text = (body.input or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty 'input'")

    try:
        audio, sr = synthesize_np(
            text=text,
            voice=body.voice,
            speed=body.speed if body.speed is not None else settings.default_speed,
            lang_code=body.lang_code or settings.lang_code,
            sample_rate=body.sample_rate or settings.default_sample_rate,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kokoro synth failed: {e}")

    # Optional save
    try:
        _ = maybe_save(
            audio=audio,
            sr=sr,
            basename="out",  # you can add timestamp/uuid if you want per-request files
            enable=body.save if body.save is not None else settings.save_audio,
        )
    except Exception:
        # saving should never break the request
        pass

    # Encode final
    try:
        blob, ctype = encode_audio(audio, sr, fmt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoding failed: {e}")

    return Response(content=blob, media_type=ctype)
