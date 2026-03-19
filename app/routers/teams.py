from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, database
from app.core import deps
# 👇 Yeni oluşturduğumuz şemayı çağırıyoruz
from app.schemas import team as team_schema 

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

@router.post("/", response_model=team_schema.TeamOut)
def create_team(
    team_in: team_schema.TeamCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        raise HTTPException(403, "Yetkisiz")
        
    team = models.Team(name=team_in.name, leader_id=team_in.leader_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # Çıktı formatına dönüştür
    return prepare_team_out(team)

@router.get("/", response_model=List[team_schema.TeamOut])
def get_teams(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    teams = db.query(models.Team).all()
    # Her bir takımı özel formata çevirip liste olarak döndür
    return [prepare_team_out(t) for t in teams]

@router.put("/{team_id}/leader")
def assign_leader(
    team_id: int,
    data: dict, # {"leader_id": 5}
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]: raise HTTPException(403, "Yetkisiz")
    
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team: raise HTTPException(404, "Takım yok")
    
    team.leader_id = data.get("leader_id")
    db.commit()
    return {"message": "Lider atandı"}

# 👇 PERSONELİ TAKIMA EKLEME (Frontend'de 'Düzenle'den yapıyoruz ama burası da dursun)
@router.put("/assign/{employee_id}")
def assign_employee_to_team(
    employee_id: int,
    team_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]: raise HTTPException(403, "Yetkisiz")
    
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp: raise HTTPException(404, "Personel yok")
    
    emp.team_id = team_id
    db.commit()
    return {"message": "Personel takıma eklendi"}

# 🛠️ YARDIMCI FONKSİYON: Veritabanı Nesnesini -> Site Paketine Çevirir
def prepare_team_out(t):
    # Üyelerin isimlerini listeye çevir
    member_names = [f"{m.first_name} {m.last_name}" for m in t.members]
    
    leader_name = None
    if t.leader:
        leader_name = f"{t.leader.first_name} {t.leader.last_name}"

    return team_schema.TeamOut(
        id=t.id,
        name=t.name,
        leader_id=t.leader_id,
        leader_name=leader_name,
        member_count=len(t.members),
        members=member_names # ✅ Artık isim listesi gidiyor!
    )