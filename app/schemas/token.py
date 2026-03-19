from pydantic import BaseModel
from typing import Optional

# Giriş yapınca dönecek olan veri formatı
class Token(BaseModel):
    access_token: str
    token_type: str

# Token çözüldüğünde içinden çıkacak veri formatı
class TokenData(BaseModel):
    email: Optional[str] = None