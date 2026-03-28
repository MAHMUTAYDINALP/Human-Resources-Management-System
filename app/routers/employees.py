from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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

# 2. YENİ PERSONEL EKLE ✅
@router.post("/", response_model=employee_schema.EmployeeOut)
def create_employee(
    employee_in: employee_schema.EmployeeCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # 🛡️ YETKİ KONTROLÜ
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Yetkisiz işlem.")

    # 📧 EMAIL KONTROLÜ
    if db.query(models.User).filter(models.User.email == employee_in.email).first():
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")

    try:
        # 1. KULLANICI HESABI OLUŞTUR
        new_user = models.User(
            email=employee_in.email,
            password_hash=security.get_password_hash(employee_in.password),
            role=employee_in.role
        )
        db.add(new_user)
        db.flush() # ID almak için hafızaya yaz

        # 🧮 İZİN HAKLARINI HESAPLA
        annual_limit = 14 
        if employee_in.role in ["Memur", "Yazılımcı", "İnsan Kaynakları", "Mühendis"]:
            annual_limit = 20
        elif employee_in.role in ["Satış Müdürü", "Genel Müdür", "Yönetici", "CEO"]:
            annual_limit = 30

        # 2. PERSONEL KARTINI OLUŞTUR
        # NOT: Eğer department_id veya employment_type_id boş gelirse varsayılan 1 değerini atar.

        
        # 2. PERSONEL KARTINI OLUŞTUR (Maaş Mantığı Eklenmiş Hali)

# Maaş belirleme mantığı (Junior Pro Dokunuşu)
        base_salary = 17002
        if employee_in.role == "Yazılımcı":
            base_salary = 45000
        elif employee_in.role == "İnsan Kaynakları":
            base_salary = 35000
        elif employee_in.role == "Satış Müdürü":
            base_salary = 55000
        elif employee_in.role == "Memur":
            base_salary = 25000
        elif employee_in.role == "Yönetici":
            base_salary = 75000

        new_emp = models.Employee(
            user_id=new_user.id,
            first_name=employee_in.first_name,
            last_name=employee_in.last_name,
            department_id=employee_in.department_id if employee_in.department_id else 1,
            employment_type_id=employee_in.employment_type_id if employee_in.employment_type_id else 1,
            gender=employee_in.gender,
            birth_date=employee_in.birth_date,
            role=employee_in.role,
            salary=base_salary, # 👈 Sabit rakam yerine değişkeni yazdık!
            annual_leave_entitlement=annual_limit, 
            excuse_leave_entitlement=7,
            sick_leave_entitlement=30
        )
        db.add(new_emp)
        db.commit() # Her şey tamamsa veritabanına işle
        db.refresh(new_emp)
        return new_emp

    except Exception as e:
        db.rollback() # Hata olursa yapılanları geri al (User tablosu kirlenmesin)
        print(f"HATA OLUŞTU: {str(e)}") # Terminalde hatayı gör
        raise HTTPException(status_code=500, detail=f"Personel oluşturulamadı: {str(e)}")

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

# 4. PERSONEL BİLGİLERİNİ GÜNCELLE
@router.put("/{employee_id}")
def update_employee(
    employee_id: int,
    emp_in: employee_schema.EmployeeUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Yetkisiz.")

    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp: raise HTTPException(404, "Bulunamadı")

    update_data = emp_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(emp, key, value)
    
    db.commit()
    return {"message": "Güncellendi"}

# 5. PERSONEL SİL
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
    
    db.delete(emp)
    if user: db.delete(user)
    
    db.commit()
    return {"message": "Personel ve hesabı silindi."}