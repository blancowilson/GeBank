from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeBankSaint"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # DB Settings
    SQL_SERVER_URL: str
    
    # Celery & Redis
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
