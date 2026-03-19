from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
# 👇 İŞTE EKSİK OLAN TANIMLAR BURADA:
from app.db import models, database 
from app.schemas import employee as employee_schema
from app.core import deps, security

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# 1. TÜM PERSONELİ GETİR
@router.get("/", response_model=List[employee_schema.EmployeeOut])
def get_employees(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    employees = db.query(models.Employee).all()
    return employees

# 2. YENİ PERSONEL EKLE (Otomatik İzin Tanımlı Versiyon ✅)
@router.post("/", response_model=employee_schema.EmployeeOut)
def create_employee(
    employee_in: employee_schema.EmployeeCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # 🛡️ YETKİ KONTROLÜ (Sadece İK ve Admin ekleyebilir)
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Yetkisiz işlem.")

    # 📧 EMAIL KONTROLÜ (Aynı mailden var mı?)
    if db.query(models.User).filter(models.User.email == employee_in.email).first():
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")

    # 1. KULLANICI HESABI OLUŞTUR (Giriş Yapabilmesi İçin)
    new_user = models.User(
        email=employee_in.email,
        password_hash=security.get_password_hash(employee_in.password),
        role=employee_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🧮 İZİN HAKLARINI HESAPLA (Senin Kuralların)
    
    # KURAL 1: Mazeret ve Rapor SABİT (Herkese Eşit)
    excuse_limit = 7
    sick_limit = 30

    # KURAL 2: Yıllık İzin RÖLE GÖRE DEĞİŞKEN
    # Varsayılan (İşçi vb.)
    annual_limit = 14 
    
    # Orta Kademe (Memur, Yazılımcı, İK)
    if employee_in.role in ["Memur", "Yazılımcı", "İnsan Kaynakları", "Mühendis"]:
        annual_limit = 20
        
    # Üst Kademe (Müdürler, Yöneticiler)
    elif employee_in.role in ["Satış Müdürü", "Genel Müdür", "Yönetici", "CEO"]:
        annual_limit = 30

    # 2. PERSONEL KARTINI OLUŞTUR
    new_emp = models.Employee(
        user_id=new_user.id,
        first_name=employee_in.first_name,
        last_name=employee_in.last_name,
        department_id=employee_in.department_id,
        employment_type_id=employee_in.employment_type_id,
        gender=employee_in.gender,
        birth_date=employee_in.birth_date,
        role=employee_in.role,
        salary=17002, # Başlangıç maaşı (Sonradan düzenlenebilir)
        
        # 👇 HESAPLANAN İZİNLERİ KAYDET
        annual_leave_entitlement=annual_limit, 
        excuse_leave_entitlement=excuse_limit,
        sick_leave_entitlement=sick_limit
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    
    return new_emp

# 3. MAAŞ GÜNCELLEME
@router.put("/{employee_id}/salary")
def update_salary(
    employee_id: int,
    salary_data: dict,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Yetkisiz.")
        
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Personel bulunamadı.")
        
    emp.salary = salary_data.get("amount")
    db.commit()
    return {"message": "Maaş güncellendi"}

# 4. PERSONEL BİLGİLERİNİ GÜNCELLE (Düzenle Modu İçin)
# 4. PERSONEL BİLGİLERİNİ GÜNCELLE
@router.put("/{employee_id}")
def update_employee(
    employee_id: int,
    emp_in: employee_schema.EmployeeUpdate, # 👈 DİKKAT: Burayı değiştirdik! (EmployeeCreate -> EmployeeUpdate)
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Yetkisiz.")

    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp: raise HTTPException(404, "Bulunamadı")

    # Gelen veride hangi alanlar doluysa onları güncelle
    update_data = emp_in.dict(exclude_unset=True) # Sadece gönderilenleri al
    
    for key, value in update_data.items():
        setattr(emp, key, value)
    
    db.commit()
    return {"message": "Güncellendi"}


# 5. PERSONEL SİL (User ile birlikte)
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Sadece Admin silebilir.")

    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp: raise HTTPException(404, "Bulunamadı")
    
    user = db.query(models.User).filter(models.User.id == emp.user_id).first()
    
    # Önce Personel Kartını Sil
    db.delete(emp)
    # Sonra Kullanıcı Hesabını Sil
    if user: db.delete(user)
    
    db.commit()
    return {"message": "Personel ve hesabı silindi."}