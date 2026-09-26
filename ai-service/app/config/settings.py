"""AI Service Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """AI Service settings loaded from environment"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Server
    AI_SERVICE_HOST: str = "0.0.0.0"
    AI_SERVICE_PORT: int = 8001
    AI_SERVICE_ENV: str = "development"
    
    # Backend API
    BACKEND_API_URL: str = "http://localhost:8000"
    BACKEND_API_TOKEN: str = ""  # JWT token for authenticated requests
    BACKEND_SERVICE_EMAIL: str = ""  # Service account email for auto-login
    BACKEND_SERVICE_PASSWORD: str = ""  # Service account password
    
    # AI Provider
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Model Config
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gpt-4o-mini"
    GEMINI_MODEL: str = "gemini-3.8-flash"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2000
    
    # Feature Flags
    ENABLE_REAL_ML_MODELS: bool = False
    ENABLE_LANGSMITH_TRACING: bool = False
    AI_SERVICE_MODE: str = "real"  # "real" or "demo" - controls fallback behavior
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Prediction Config
    PREDICTION_HORIZON_MINUTES: int = 60  # default horizon in minutes
    PREDICTION_MIN_HISTORY: int = 30  # minimum number of metric records required

    # Existing fields continue unchanged
settings = Settings()
