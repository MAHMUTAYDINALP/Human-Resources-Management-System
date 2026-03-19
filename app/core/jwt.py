from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

# BU BİLGİLER ÇOK GİZLİDİR! Gerçek projede bunları gizli dosyalardan okuruz.
# Şimdilik buraya yazıyoruz.
SECRET_KEY = "cok-gizli-ve-uzun-bir-kelime-dizisi-buraya-yazilacak"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Bilet 30 dakika geçerli olsun

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Kullanıcı için süreli bir giriş bileti (Token) oluşturur."""
    to_encode = data.copy()
    
    # Biletin son kullanma tarihini belirle
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Tarihi bilete ekle
    to_encode.update({"exp": expire})
    
    # Bileti gizli anahtarla mühürle (şifrele)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt