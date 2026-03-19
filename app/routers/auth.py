from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security, deps
from app.core.config import settings
from app.db import models, database
from app.schemas import token as token_schema

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=token_schema.Token)
def login_access_token(
    db: Session = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = security.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Hatalı email veya şifre")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Kullanıcı aktif değil")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

# 👇 GÜNCELLENEN FONKSİYON BURASI ✅
@router.get("/me")
def read_users_me(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    # Kullanıcının Personel Kartını Bul
    emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role, 
        "employee_id": emp.id if emp else None,
        "first_name": emp.first_name if emp else "Yönetici",
        "last_name": emp.last_name if emp else "",
        "job_title": emp.role if emp else "Yönetici", 
        "team_id": emp.team_id if emp else None,

        # 👇 İZİN HAKLARINI ARTIK GÖNDERİYORUZ!
        "annual_leave_entitlement": emp.annual_leave_entitlement if emp else 0,
        "excuse_leave_entitlement": emp.excuse_leave_entitlement if emp else 0,
        "sick_leave_entitlement": emp.sick_leave_entitlement if emp else 0
    }