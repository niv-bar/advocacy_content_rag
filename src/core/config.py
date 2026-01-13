"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    APP_NAME: str = "RiseApp RAG"
    DATA_DIR: str = "data"

    # API Keys (from .env)
    OPENAI_API_KEY: str = ""
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()

# from pydantic_settings import BaseSettings, SettingsConfigDict
#
# class Settings(BaseSettings):
#     # App Config
#     APP_NAME: str = "RiseApp RAG"
#
#     # API Keys (These must be in your .env file)
#     # We make them optional for now so the code doesn't crash if .env is empty during testing
#     OPENAI_API_KEY: str = ""
#     QDRANT_URL: str = ""
#     QDRANT_API_KEY: str = ""
#
#     # Paths
#     DATA_DIR: str = "data"
#
#     # Load from .env file automatically
#     model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")
#
# # Export a single instance
# settings = Settings()