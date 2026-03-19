from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 👇 SADECE KALAN DOSYALARI ÇAĞIR
from app.routers import auth, employees, leaves, dashboard, announcements, teams
from app.core import config

app = FastAPI(title="İK Yönetim Sistemi")

# CORS Ayarları (Dokunma)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 SİLİNENLERİ BURADAN DA ÇIKAR (payrolls, performance, users, departments YOK)
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(dashboard.router)
app.include_router(announcements.router)
app.include_router(teams.router)

@app.get("/")
def read_root():
    return {"message": "İK Yönetim Sistemi API Çalışıyor 🚀"}