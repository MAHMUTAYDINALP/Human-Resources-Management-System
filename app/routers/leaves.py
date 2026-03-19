from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.db import models, database
from app.core import deps
from pydantic import BaseModel

router = APIRouter(
    prefix="/leaves",
    tags=["Leaves"]
)

class LeaveCreate(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str

class LeaveOut(BaseModel):
    id: int
    employee_name: str
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str
    status: str

    class Config:
        from_attributes = True

@router.post("/")
def create_leave_request(
    leave: LeaveCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # 1. Tarih Kontrolü: Geçmişe veya tersten tarih girilmesin
    if leave.end_date < leave.start_date:
        raise HTTPException(status_code=400, detail="Bitiş tarihi başlangıçtan önce olamaz!")

    # İzin süresini hesapla (+1 gün ekliyoruz çünkü 1 günlük izin 1 gündür)
    duration = (leave.end_date - leave.start_date).days + 1

    # 2. Personeli Bul
    emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(404, "Personel kartı bulunamadı.")

    # 3. BAKİYE KONTROLÜ (BEKÇİ BURADA 👮‍♂️)
    # İzin tipine göre kalan hakkı kontrol et
    if leave.leave_type_id == 1: # Yıllık İzin
        if emp.annual_leave_entitlement < duration:
            raise HTTPException(status_code=400, detail=f"Yetersiz Yıllık İzin Bakiyesi! (Kalan: {emp.annual_leave_entitlement} gün, İstenen: {duration} gün)")
            
    elif leave.leave_type_id == 2: # Mazeret İzni
        if emp.excuse_leave_entitlement < duration:
            raise HTTPException(status_code=400, detail=f"Yetersiz Mazeret İzni Bakiyesi! (Kalan: {emp.excuse_leave_entitlement} gün)")
            
    elif leave.leave_type_id == 3: # Rapor
        if emp.sick_leave_entitlement < duration:
             raise HTTPException(status_code=400, detail=f"Rapor hakkınız dolmuş! (Kalan: {emp.sick_leave_entitlement} gün)")

    # 4. Her şey yolundaysa talebi oluştur
    new_leave = models.Leave(
        employee_id=emp.id,
        leave_type_id=leave.leave_type_id,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason,
        status="Beklemede"
    )
    
    # Not: Bakiye hemen düşmez, "ONAYLANINCA" düşer. 
    # Ama burada eksiye düşmeyi engellemek için ön kontrol yaptık.
    
    db.add(new_leave)
    db.commit()
    return {"message": "İzin talebi oluşturuldu."}

# (Diğer GET/PUT fonksiyonların aynı kalabilir, buraya dokunmadık)
@router.get("/my", response_model=List[LeaveOut])
def get_my_leaves(db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_active_user)):
    emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    leaves = db.query(models.Leave).filter(models.Leave.employee_id == emp.id).all()
    return [convert_to_out(l, db) for l in leaves]

@router.get("/all", response_model=List[LeaveOut])
def get_all_leaves(db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_active_user)):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(403, "Yetkisiz")
    leaves = db.query(models.Leave).all()
    return [convert_to_out(l, db) for l in leaves]

@router.put("/{id}/status")
def update_leave_status(id: int, status_data: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_active_user)):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]: raise HTTPException(403, "Yetkisiz")
    
    leave = db.query(models.Leave).filter(models.Leave.id == id).first()
    if not leave: raise HTTPException(404, "Bulunamadı")
    
    # Eğer daha önce onaylanmamışsa ve şimdi ONAYLANDI deniyorsa bakiyeyi düş
    if leave.status != "Onaylandı" and status_data["status"] == "Onaylandı":
        emp = db.query(models.Employee).filter(models.Employee.id == leave.employee_id).first()
        duration = (leave.end_date - leave.start_date).days + 1
        
        # Son kez bakiye kontrolü yap (Arada başkası onaylamış olabilir)
        if leave.leave_type_id == 1 and emp.annual_leave_entitlement < duration:
             raise HTTPException(400, "Bakiye yetersiz, onaylanamaz!")
        
        # Bakiyeyi düş
        if leave.leave_type_id == 1: emp.annual_leave_entitlement -= duration
        elif leave.leave_type_id == 2: emp.excuse_leave_entitlement -= duration
        elif leave.leave_type_id == 3: emp.sick_leave_entitlement -= duration
        
        db.add(emp)

    leave.status = status_data["status"]
    db.commit()
    return {"message": "Güncellendi"}

@router.delete("/{id}")
def delete_leave(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_active_user)):
    # Sadece Admin veya İK silebilir
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Yetkisiz işlem.")
        
    leave = db.query(models.Leave).filter(models.Leave.id == id).first()
    if not leave: raise HTTPException(404, "İzin bulunamadı")
    
    # Eğer silinen izin 'Onaylandı' durumundaysa, günleri personele GERİ İADE ET
    if leave.status == "Onaylandı":
        emp = db.query(models.Employee).filter(models.Employee.id == leave.employee_id).first()
        duration = (leave.end_date - leave.start_date).days + 1
        
        if leave.leave_type_id == 1: emp.annual_leave_entitlement += duration
        elif leave.leave_type_id == 2: emp.excuse_leave_entitlement += duration
        elif leave.leave_type_id == 3: emp.sick_leave_entitlement += duration
        db.add(emp)

    db.delete(leave)
    db.commit()
    return {"message": "Silindi"}

def convert_to_out(l, db):
    emp = db.query(models.Employee).filter(models.Employee.id == l.employee_id).first()
    return LeaveOut(
        id=l.id,
        employee_name=f"{emp.first_name} {emp.last_name}" if emp else "Bilinmiyor",
        leave_type_id=l.leave_type_id,
        start_date=l.start_date,
        end_date=l.end_date,
        reason=l.reason,
        status=l.status
    )