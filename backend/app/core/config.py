import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    print(f"Warning: Could not find .env file at {ENV_PATH}")

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    ENCRYPTION_KEY: str

    USE_MOCK_DATA: bool = False

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        # FIXED: Pydantic v2 BaseSettings freezes models by default.
        # Without this, "settings.USE_MOCK_DATA = True" in settings.py route
        # is silently ignored on some versions — the value never actually changes
        # in memory, so the demo mode toggle appears to work (returns the new value
        # from the endpoint) but the NEXT request to /api/sync/ still reads the
        # OLD frozen value. frozen=False makes the assignment stick reliably.
        frozen=False,
    )

settings = Settings()
