from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DATABASE_USER: str
    # DATABASE_PASSWORD: str
    # DATABASE_HOST: str
    # DATABASE_PORT: int
    # DATABASE_NAME: str
    DATABASE_URL: str
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str

    # Security settings
    PASSWORD_PEPPER: str

    def get_database_url(self) -> str:
        return f"{self.DATABASE_URL}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()