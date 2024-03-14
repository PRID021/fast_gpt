from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    INSTANCE_CONNECTION_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    PRIVATE_IP: bool
    DB_URI: str
settings = Settings(
    _env_file=Path(__file__).parent / "../.env", _env_file_encoding="utf-8"
)
