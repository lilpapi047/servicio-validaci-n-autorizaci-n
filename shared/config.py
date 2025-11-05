from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "5689"
    resend_api_key: str   # 👈 nuevo campo
    frontend_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()