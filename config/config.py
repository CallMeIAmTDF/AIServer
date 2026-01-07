from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_protocol: str = "http"
    api_port: str = "8000"
    api_host: str = "0.0.0.0"

    gemini_key: str
    groq_key: str

    gemini_key2: Optional[str] = None
    gemini_key3: Optional[str] = None
    gemini_key4: Optional[str] = None
    gemini_key5: Optional[str] = None
    gemini_key6: Optional[str] = None
    stored: Optional[str] = "fileSearchStores/algo-store-bazsklvllb48"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()