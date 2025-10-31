# app/core/config.py  (Pydantic v2)
from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tell pydantic-settings to load .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Server
    app_name: str = "Kokoro OpenAI-Compatible TTS"
    debug: bool = Field(False, alias="DEBUG")
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8080, alias="PORT")

    # CORS
    cors_enabled: bool = Field(True, alias="CORS_ENABLED")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")

    # Kokoro defaults
    lang_code: str = Field("a", alias="KOKORO_LANG_CODE")              # a(US-EN), b(UK-EN), h(Hindi), …
    default_voice: str = Field("af_heart", alias="KOKORO_DEFAULT_VOICE")
    default_speed: float = Field(1.0, alias="KOKORO_DEFAULT_SPEED")
    default_sample_rate: int = Field(24000, alias="KOKORO_SAMPLE_RATE")

    # Storage
    save_audio: bool = Field(True, alias="SAVE_AUDIO")
    save_dir: str = Field("app/assets/out", alias="SAVE_DIR")

    # Formats
    allowed_formats: List[str] = Field(
        default_factory=lambda: ["wav", "mp3", "ogg", "flac"],
        alias="ALLOWED_FORMATS",
    )

@lru_cache
def get_settings() -> "Settings":
    return Settings()

settings = get_settings()
