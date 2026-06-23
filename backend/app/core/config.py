from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # New JWT Secrets
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    ENCRYPTION_KEY: str

    USE_MOCK_DATA: bool = False

    # This tells Python to look for the .env file in the current directory
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# We create one instance of this to use throughout our app
settings = Settings()