from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers.openai_compatible import router as openai_router
from kokoro import KPipeline
import os

app = FastAPI(title=settings.app_name, debug=settings.debug)

if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(openai_router)


@app.on_event("startup")
async def preload_kokoro_voices():
    """Automatically preload Kokoro voices on startup (first run)."""
    voices = os.getenv("KOKORO_PRELOAD_VOICES", "").split()
    if not voices:
        print("No KOKORO_PRELOAD_VOICES defined, skipping preload.")
        return
    pipe = KPipeline(lang_code=settings.lang_code)
    print(f"Preloading Kokoro voices: {voices}")
    for v in voices:
        try:
            list(pipe("hello world", voice=v))
            print(f" Cached voice: {v}")
        except Exception as e:
            print(f"Failed to preload {v}: {e}")


@app.get("/healthz")
def healthz():
    return {"ok": True, "lang": settings.lang_code, "voice": settings.default_voice}
