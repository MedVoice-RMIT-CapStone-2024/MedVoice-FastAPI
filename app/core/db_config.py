import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@db/nurses_db")

settings = Settings()

class VectorSettings(BaseSettings):
    DATABASE_URL: str = os.getenv("VECTOR_DATABASE_URL", "postgresql+psycopg2://postgres:password@pgvector-db/vector_db")

vector_settings = VectorSettings()
