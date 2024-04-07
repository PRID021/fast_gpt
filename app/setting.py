from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    DB_URI: str


settings = Settings(
    _env_file=Path(__file__).parent / "../.env",
    _env_file_encoding="utf-8",
)


print("17:", settings)
