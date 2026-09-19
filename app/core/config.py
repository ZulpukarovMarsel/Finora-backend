"""
Central app configuration. All values are overridable via environment
variables / .env, which is how docker-compose wires things up.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Finora API"
    API_V1_PREFIX: str = "/api/v1"

    POSTGRES_USER: str = "finora"
    POSTGRES_PASSWORD: str = "finora"
    POSTGRES_DB: str = "finora"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    SECRET_KEY: str = "change-me-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14

    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
