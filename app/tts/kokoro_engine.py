# app/tts/kokoro_engine.py
import io
import os
from typing import Optional, Tuple

import numpy as np

from app.core.config import settings

# Kokoro
from kokoro import KPipeline

# Encoders
import soundfile as sf  # wav/flac/ogg via libsndfile
from pydub import AudioSegment  # mp3/ogg if ffmpeg present

# Singleton pipeline (lazy init)
_PIPELINE: Optional[KPipeline] = None
_LANG_IN_USE: Optional[str] = None

def _get_pipeline(lang_code: str) -> KPipeline:
    global _PIPELINE, _LANG_IN_USE
    if _PIPELINE is None or _LANG_IN_USE != lang_code:
        _PIPELINE = KPipeline(lang_code=lang_code)
        _LANG_IN_USE = lang_code
    return _PIPELINE

def _as_float32_mono(x) -> np.ndarray:
    """Kokoro yields chunks as tensors/arrays → 1-D float32 [-1,1]."""
    import numpy as _np
    import torch as _torch
    if isinstance(x, _torch.Tensor):
        x = x.detach().cpu().numpy()
    a = _np.asarray(x, dtype=_np.float32).reshape(-1)
    return a

def synthesize_np(
    text: str,
    voice: Optional[str] = None,
    speed: float = 1.0,
    lang_code: Optional[str] = None,
    sample_rate: Optional[int] = None,
) -> Tuple[np.ndarray, int]:
    """
    Returns (audio_float32_mono, sr).
    Streams chunks from Kokoro and concatenates; still fast and safe server-side.
    """
    voice = voice or settings.default_voice
    lang_code = lang_code or settings.lang_code
    sr = int(sample_rate or settings.default_sample_rate)

    pipe = _get_pipeline(lang_code=lang_code)

    chunks = []
    gen = pipe(text, voice=voice, speed=speed, split_pattern=r"\n+")
    for (_gs, _ps, audio) in gen:
        chunks.append(_as_float32_mono(audio))

    if not chunks:
        return np.zeros(0, dtype=np.float32), sr

    import numpy as np
    audio = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
    return audio, sr

def _encode_wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()

def _encode_flac_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="FLAC")
    return buf.getvalue()

def _encode_ogg_bytes(audio: np.ndarray, sr: int) -> bytes:
    # OGG Vorbis via libsndfile (if supported)
    buf = io.BytesIO()
    try:
        sf.write(buf, audio, sr, format="OGG", subtype="VORBIS")
        return buf.getvalue()
    except Exception:
        # Fallback to pydub/ffmpeg if libsndfile lacks vorbis
        seg = AudioSegment(
            (audio * 32767.0).astype(np.int16).tobytes(),
            frame_rate=sr,
            sample_width=2,
            channels=1,
        )
        out = io.BytesIO()
        seg.export(out, format="ogg")
        return out.getvalue()

def _encode_mp3_bytes(audio: np.ndarray, sr: int) -> bytes:
    # Requires ffmpeg (installed in Dockerfile)
    seg = AudioSegment(
        (audio * 32767.0).astype(np.int16).tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1,
    )
    out = io.BytesIO()
    seg.export(out, format="mp3")
    return out.getvalue()

def encode_audio(audio: np.ndarray, sr: int, fmt: str) -> Tuple[bytes, str]:
    fmt = (fmt or "wav").lower()
    if fmt == "wav":
        return _encode_wav_bytes(audio, sr), "audio/wav"
    if fmt == "flac":
        return _encode_flac_bytes(audio, sr), "audio/flac"
    if fmt == "ogg":
        return _encode_ogg_bytes(audio, sr), "audio/ogg"
    if fmt == "mp3":
        return _encode_mp3_bytes(audio, sr), "audio/mpeg"

    # Fallback to wav
    return _encode_wav_bytes(audio, sr), "audio/wav"

def maybe_save(audio: np.ndarray, sr: int, basename: str, enable: bool) -> Optional[str]:
    if not enable:
        return None
    os.makedirs(settings.save_dir, exist_ok=True)
    path = os.path.join(settings.save_dir, f"{basename}.wav")
    sf.write(path, audio, sr, format="WAV", subtype="PCM_16")
    return path
