from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Document Processing Service"
    app_version: str = "0.1.0"
    debug: bool = False

    # PostgreSQL configuration
    postgres_user: str = "exemple"
    postgres_password: str = "exemple"
    postgres_db: str = "exemple"
    postgres_host: str = "exemple"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Celery configuration
    celery_broker_url: str = "exemple"
    celery_result_backend: str = "exemple"
    tesseract_path: str = "exemple"
        
    class Config:
        env_file = ".env"

settings = Settings()