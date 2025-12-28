from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeBankSaint"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # DB Settings (will be configured later)
    # SQL_SERVER_URL: str
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
