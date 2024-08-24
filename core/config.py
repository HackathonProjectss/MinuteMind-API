from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict
from pydantic import AnyHttpUrl
from core.logger import logger
from decouple import config
class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    PROJECT_NAME: str = "FastAPI"
    BASE_URL: str = config('BASE_URL', cast=str)
    WATSONX_API_KEY: str = config('WATSONX_API_KEY', cast=str)
    OPENAI_API_KEY: str = config('OPENAI_API_KEY', cast=str)
    WATSONX_BASE_URL: str = config('WATSONX_BASE_URL', cast=str)
    WATSONX_VERSION: str = config('WATSONX_VERSION', cast=str)
    WATSONX_PROJECT_ID: str = config('WATSONX_PROJECT_ID', cast=str)    
    class Config:
        case_sensitive = True
    
settings = Settings()
