from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # This tells Python to look for the .env file in the current directory
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# We create one instance of this to use throughout our app
settings = Settings()