from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "İK Yönetim Sistemi"
    
  
    DATABASE_URL: str = "postgresql://postgres:12345@localhost/ik_yonetim_db"
    
    # GÜVENLİK AYARLARI
    SECRET_KEY: str = "cok_gizli_ve_uzun_bir_rastgele_metin_buraya_yaz" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()