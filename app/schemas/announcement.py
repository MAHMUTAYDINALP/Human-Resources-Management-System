from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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