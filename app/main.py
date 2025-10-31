# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.openai_compatible import router as openai_router

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

@app.get("/healthz")
def healthz():
    return {"ok": True, "lang": settings.lang_code, "voice": settings.default_voice}
