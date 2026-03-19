from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime # 👈 BU GEREKLİ
from app.db import models, database
from app.core import deps
from pydantic import BaseModel

router = APIRouter(
    prefix="/announcements",
    tags=["Announcements"]
)

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    is_public: bool = False
    target_team_id: Optional[int] = None

class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author_name: str
    is_public: bool
    target_team_name: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/", response_model=AnnouncementOut)
def create_announcement(
    ann: AnnouncementCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # Gönderen kişinin personel kartını bul
    author = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Personel kaydı bulunamadı.")

    # YETKİ KONTROLÜ
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
        # 1. Genel Duyuru (Public) yapamaz
        if ann.is_public:
            raise HTTPException(status_code=403, detail="Genel duyuru yapma yetkiniz yok.")
        
        # 2. Takım Duyurusu yapıyorsa, O TAKIMIN LİDERİ olmalı
        if ann.target_team_id:
            team = db.query(models.Team).filter(models.Team.id == ann.target_team_id).first()
            if not team:
                raise HTTPException(404, "Takım bulunamadı.")
            
            if team.leader_id != author.id:
                raise HTTPException(status_code=403, detail="Sadece lideri olduğunuz takıma duyuru yapabilirsiniz!")
        else:
            raise HTTPException(status_code=400, detail="Bir hedef kitle (Takım) seçmelisiniz.")

    new_ann = models.Announcement(
        title=ann.title,
        content=ann.content,
        author_id=author.id,
        is_public=ann.is_public,
        target_team_id=ann.target_team_id,
        # 👇 HATAYI ÇÖZEN KISIM BURASI: Tarihi biz veriyoruz, DB'yi beklemiyoruz.
        created_at=datetime.now() 
    )
    db.add(new_ann)
    db.commit()
    db.refresh(new_ann)
    return convert_to_out(new_ann, db)

@router.get("/", response_model=List[AnnouncementOut])
def get_announcements(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    user_emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    
    query = db.query(models.Announcement)
    
    if current_user.role in ["admin", "hr", "İnsan Kaynakları"]:
        anns = query.order_by(models.Announcement.created_at.desc()).all()
    else:
        team_id = user_emp.team_id if user_emp else -1
        anns = query.filter(
            (models.Announcement.is_public == True) | 
            (models.Announcement.target_team_id == team_id)
        ).order_by(models.Announcement.created_at.desc()).all()

    return [convert_to_out(a, db) for a in anns]

@router.delete("/{id}")
def delete_announcement(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # Silme yetkisi sadece admin ve HR'da olsun (Veya istersen lider kendi duyurusunu silsin diye güncelleyebiliriz)
    if current_user.role not in ["admin", "hr", "İnsan Kaynakları"]:
         raise HTTPException(status_code=403, detail="Yetkisiz.")
         
    ann = db.query(models.Announcement).filter(models.Announcement.id == id).first()
    if not ann: raise HTTPException(404, "Bulunamadı")
    
    db.delete(ann)
    db.commit()
    return {"message": "Silindi"}

def convert_to_out(ann, db):
    author = db.query(models.Employee).filter(models.Employee.id == ann.author_id).first()
    team_name = None
    if ann.target_team_id:
        t = db.query(models.Team).filter(models.Team.id == ann.target_team_id).first()
        team_name = t.name if t else None

    return AnnouncementOut(
        id=ann.id,
        title=ann.title,
        content=ann.content,
        created_at=ann.created_at, # Artık burası dolu gelecek ✅
        author_name=f"{author.first_name} {author.last_name}" if author else "Bilinmiyor",
        is_public=ann.is_public,
        target_team_name=team_name
    )