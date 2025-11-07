from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "5689"
    resend_api_key: str   
    frontend_url: str
    register_service_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()