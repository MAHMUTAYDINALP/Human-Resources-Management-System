from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.db import models, database
from app.core import deps

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard (İstatistik Paneli)"]
)

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # 1. YETKİ KONTROLÜ
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(status_code=403, detail="Bu verileri görme yetkiniz yok.")

    # 2. TOPLAM ÇALIŞAN
    total_employees = db.query(models.Employee).count()

    # 3. CİNSİYET ORANI
    gender_query = db.query(models.Employee.gender, func.count(models.Employee.id)).group_by(models.Employee.gender).all()
    gender_stats = {g[0]: g[1] for g in gender_query if g[0]} 

    # 4. İZİN DURUMU (AKTİF VE GELECEK) - GÜNCELLENDİ ✅
    today = date.today()
    leave_types_map = {1: "Yıllık İzin", 2: "Mazeret İzni", 3: "Rapor"}

    # Bitiş tarihi bugün veya daha ileri olan (Henüz bitmemiş) tüm onaylı izinleri çek
    # Tarihe göre sırala ki en yakın olan en üstte çıksın
    leaves_query = db.query(models.Leave).filter(
        models.Leave.status == "Onaylandı",
        models.Leave.end_date >= today
    ).order_by(models.Leave.start_date.asc()).all()
    
    dashboard_leaves = []
    for leave in leaves_query:
        emp = db.query(models.Employee).filter(models.Employee.id == leave.employee_id).first()
        if emp:
            # Durumu Belirle: Şu an mı tatilde, yoksa ileri tarihli mi?
            is_active = leave.start_date <= today and leave.end_date >= today
            status_label = "Şu an İzinli" if is_active else "Planlanmış"
            
            dashboard_leaves.append({
                "name": f"{emp.first_name} {emp.last_name}",
                "role": emp.role,
                "type_name": leave_types_map.get(leave.leave_type_id, "Diğer"),
                "start_date": leave.start_date.strftime("%d.%m.%Y"),
                "end_date": leave.end_date.strftime("%d.%m.%Y"),
                "status_label": status_label, # Frontend'de renk ayrımı için
                "is_active": is_active        # Sıralama veya ikon için
            })

    # 5. DOĞUM GÜNLERİ
    employees = db.query(models.Employee).all()
    upcoming_birthdays = []
    all_birthdays = []
    
    for emp in employees:
        if not emp.birth_date: continue
        try:
            this_year_bdate = date(today.year, emp.birth_date.month, emp.birth_date.day)
        except ValueError:
            this_year_bdate = date(today.year, 3, 1)

        if this_year_bdate < today:
            next_bdate = date(today.year + 1, this_year_bdate.month, this_year_bdate.day)
        else:
            next_bdate = this_year_bdate
            
        days_left = (next_bdate - today).days
        
        emp_data = {
            "name": f"{emp.first_name} {emp.last_name}",
            "birth_date": emp.birth_date.strftime("%d.%m.%Y"),
            "days_left": days_left,
            "role": emp.role
        }
        all_birthdays.append(emp_data)
        if days_left <= 30:
            upcoming_birthdays.append(emp_data)
            
    upcoming_birthdays.sort(key=lambda x: x['days_left'])

    return {
        "total": total_employees,
        "genders": gender_stats,
        "active_leaves": dashboard_leaves, # İsim değişmedi ama içeriği zenginleşti
        "upcoming_birthdays": upcoming_birthdays,
        "all_birthdays": all_birthdays
    }