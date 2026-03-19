from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session # Veritabanı bağlantısı için gerekli
from app.core.config import settings
from app.db import models # Kullanıcı tablosuna erişmek için gerekli

# Şifreleme ayarları
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    JWT Token oluşturur (Giriş anahtarı)
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Girilen şifre ile veritabanındaki şifreyi karşılaştırır.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Şifreyi kriptolar (Hash'ler).
    """
    return pwd_context.hash(password)

# 👇 EKSİK OLAN FONKSİYON BU! (EKLENDİ ✅)
def authenticate(db: Session, email: str, password: str):
    """
    Kullanıcıyı veritabanında arar ve şifresini kontrol eder.
    """
    # 1. Kullanıcıyı email ile bul
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # 2. Kullanıcı yoksa
    if not user:
        return None
    
    # 3. Şifre kontrolü
    if not verify_password(password, user.password_hash):
        return None
        
    # 4. Her şey tamamsa kullanıcıyı döndür
    return user