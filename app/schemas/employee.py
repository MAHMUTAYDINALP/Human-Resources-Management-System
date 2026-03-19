from pydantic import BaseModel
from typing import Optional
from datetime import date

# Ortak Özellikler
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    department_id: int
    employment_type_id: int
    gender: str
    birth_date: Optional[date] = None
    role: str
    team_id: Optional[int] = None

# YENİ EKLENEN SINIF (Güncelleme için esnek yapı) ✅
class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department_id: Optional[int] = None
    employment_type_id: Optional[int] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    role: Optional[str] = None
    team_id: Optional[int] = None
    # Dikkat: Şifre ve Email burada yok, çünkü onlar buradan güncellenmez.

# Oluştururken İstenenler (Şifre ve Email zorunlu)
class EmployeeCreate(EmployeeBase):
    email: str
    password: str

# Maaş Güncelleme İçin
class EmployeeUpdateSalary(BaseModel):
    amount: int

# Siteye Gönderilen Paket
class EmployeeOut(EmployeeBase):
    id: int
    user_id: int
    salary: int
    
    # E-posta User tablosundan property olarak gelir
    email: Optional[str] = None

    annual_leave_entitlement: int 
    excuse_leave_entitlement: int
    sick_leave_entitlement: int   

    class Config:
        from_attributes = True