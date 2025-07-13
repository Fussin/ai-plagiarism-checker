from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Determine the project root directory, assuming config.py is in backend/
# This allows .env and sqlite db to be at the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    APP_NAME: str = "AI Plagiarism Checker"
    DEBUG: bool = False

    # Database URL
    # Default to a SQLite database in the project root directory
    DATABASE_URL: str = f"sqlite:///{os.path.join(PROJECT_ROOT, './test.db')}"

    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # minutes

    # Paths for storing uploaded files, models, etc.
    # These paths will be relative to the project root.
    UPLOAD_DIR_NAME: str = "uploads"
    MODELS_DIR_NAME: str = "models"

    @property
    def UPLOAD_DIR(self) -> str:
        return os.path.join(PROJECT_ROOT, self.UPLOAD_DIR_NAME)

    @property
    def MODELS_DIR(self) -> str:
        return os.path.join(PROJECT_ROOT, self.MODELS_DIR_NAME)

    # API Keys for external services (e.g., OpenAI, TinEye, Google)
    # Example: OPENAI_API_KEY: str = "your_openai_api_key_here"
    # TINEYE_API_KEY: Optional[str] = None
    # GOOGLE_API_KEY: Optional[str] = None
    # GOOGLE_CSE_ID: Optional[str] = None
    OPENAI_API_KEY: str | None = None

    # Stripe Settings
    STRIPE_API_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    # Price IDs from your Stripe Dashboard
    STRIPE_PRICE_ID_PRO_BASIC: str | None = None
    STRIPE_PRICE_ID_PRO_ADVANCED: str | None = None
    # Frontend URL for Stripe redirects
    FRONTEND_URL: str = "http://localhost:3000"


    # model_config allows loading from .env file
    model_config = SettingsConfigDict(env_file=os.path.join(PROJECT_ROOT, ".env"), extra='ignore')


settings = Settings()

# Create upload and model directories if they don't exist
# This should run after settings object is created.
def create_project_dirs():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    # Create subdirectories for video processing inside uploads
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "videos_raw"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "frames"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "audio"), exist_ok=True)


create_project_dirs()
