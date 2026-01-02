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
    USE_CELERY: bool = True

    # Currency Settings
    BASE_CURRENCY: str = "USD" # USD, VES, EUR
    REFERENTIAL_CURRENCY: str = "VES" # VES, USD, EUR
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
