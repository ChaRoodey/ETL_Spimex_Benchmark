from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5532
    POSTGRES_DB: str = "spimex_db"
    POSTGRES_USER: str = "spimex_user"
    POSTGRES_PASSWORD: str = "spimex"

    DOWNLOAD_CONCURRENCY: int = 10

    LOG_LEVEL: str = "INFO"

    @property
    def async_database_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f'postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )


settings = Settings()
