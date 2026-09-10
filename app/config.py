from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from the environment and .env."""

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    gemini_api_url: str = "https://generativelanguage.googleapis.com/v1beta"
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    default_model: str = "gemini-3.6-flash"
    sessions_file: Path = Path("data/sessions.json")
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
