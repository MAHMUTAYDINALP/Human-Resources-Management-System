from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re 

# 1. Ortak Özellikler
class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    role: Optional[str] = "user"

    # YENİ KURAL: Email @gov.tr ile bitmek ZORUNDA
    @field_validator('email')
    def validate_gov_email(cls, value):
        # Regex Açıklaması:
        # \.  -> Nokta işaretini özel karakter olmaktan çıkarır
        # $   -> Metnin sonu demektir (Bununla bitmeli)
        pattern = r".*@gov\.tr$"
        
        if not re.match(pattern, value):
            raise ValueError('Sadece kurumsal (@gov.tr) mail adresleri kabul edilmektedir.')
        
        return value

# 2. Kayıt Olurken (Şifre Kuralı Değişti)
class UserCreate(UserBase):
    password: str

    # YENİ KURAL: Şifre sadece 6 RAKAM olmalı
    @field_validator('password')
    def validate_password_pin(cls, value):
        # Regex Açıklaması:
        # ^   -> Başlangıç
        # \d  -> Rakam (Digit) demektir
        # {6} -> Tam olarak 6 tane olacak
        # $   -> Bitiş
        pattern = r"^\d{6}$"
        
        if not re.match(pattern, value):
            raise ValueError('Şifre (PIN) tam olarak 6 haneli bir sayı olmalıdır. (Örn: 123456)')
        
        return value

# 3. Dışarıya Gösterilecek Veri
class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True