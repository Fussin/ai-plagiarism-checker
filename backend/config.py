from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Plagiarism Checker"
    DEBUG: bool = False
    # Database URL (if using one, e.g., SQLAlchemy)
    # DATABASE_URL: str = "sqlite:///./test.db"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key"  # CHANGE THIS!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Paths for storing uploaded files, models, etc.
    UPLOAD_DIR: str = "uploads"
    MODELS_DIR: str = "models"

    # API Keys for external services (e.g., TinEye, Google)
    # TINEYE_API_KEY: str = "your_tineye_api_key"
    # GOOGLE_API_KEY: str = "your_google_api_key"
    # GOOGLE_CSE_ID: str = "your_google_cse_id"


    class Config:
        env_file = ".env" # If you use a .env file for configuration

settings = Settings()

# Create upload and model directories if they don't exist
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
