from pydantic import BaseModel, Field
from typing import List, Optional

# Takım Oluştururken İstenen
class TeamCreate(BaseModel):
    name: str
    leader_id: Optional[int] = None

# SİTEYE GÖNDERİLEN PAKET (DÜZELTİLEN KISIM ✅)
class TeamOut(BaseModel):
    id: int
    name: str
    leader_id: Optional[int] = None
    leader_name: Optional[str] = None
    
    # Üye Sayısı
    member_count: int = 0
    
    # 👇 İŞTE EKSİK OLAN LİSTE!
    # Pydantic'e diyoruz ki: "Veritabanından gelen üyeleri, isim listesine çevir."
    members: List[str] = []

    class Config:
        from_attributes = True

    # "Validator" kullanarak karmaşık veriyi basit listeye çeviriyoruz
    @staticmethod
    def resolve_members(team_obj):
        # Eğer takımın üyeleri varsa, hepsinin adını soyadını birleştirip liste yap
        return [f"{m.first_name} {m.last_name}" for m in team_obj.members]