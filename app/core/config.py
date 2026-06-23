from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://hrcopilot:hrcopilot@localhost:5432/hrcopilot"
    APP_NAME: str = "HR Copilot"
    DEBUG: bool = False
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    COHERE_API_KEY: str = ""
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
