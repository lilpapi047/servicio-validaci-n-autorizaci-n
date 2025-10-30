from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "5689"
    
    class Config:
        env_file = ".env"

settings = Settings()