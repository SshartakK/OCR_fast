from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Document Processing Service"
    app_version: str = "0.1.0"
    debug: bool = False

    # PostgreSQL configuration
    postgres_user: str = "artem"
    postgres_password: str = "root"
    postgres_db: str = "artemfastdb"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Celery configuration
    celery_broker_url: str = "pyamqp://guest:guest@localhost//"
    celery_result_backend: str = "rpc://"
    tesseract_path: str = "/usr/bin/tesseract"
        
    class Config:
        env_file = ".env"

settings = Settings()