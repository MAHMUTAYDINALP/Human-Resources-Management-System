from pydantic import BaseModel
from typing import Optional
from datetime import date

# Temel Şema
class LeaveBase(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str

# Oluşturma
class LeaveCreate(LeaveBase):
    pass

# Durum Güncelleme (ONAY/RED İÇİN BU GEREKLİ ✅)
class LeaveUpdateStatus(BaseModel):
    status: str

# Gösterme
class LeaveOut(LeaveBase):
    id: int
    employee_id: int
    status: str
    employee_name: Optional[str] = None # İK listesi için
    type_name: Optional[str] = None     # Yıllık, Mazeret vs.
    role: Optional[str] = None          # Personel rolü

    class Config:
        from_attributes = True