from app.db.database import SessionLocal, engine, Base
from app.db import models
from app.core.security import get_password_hash

# Tabloların var olduğundan emin ol
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def init():
    print("🚀 Başlangıç verileri yükleniyor...")

    # 1. Departmanları Oluştur (Hata almamak için)
    depts = ["Yazılım", "İnsan Kaynakları", "Satış", "Yönetim"]
    for d_name in depts:
        exists = db.query(models.Department).filter(models.Department.name == d_name).first()
        if not exists:
            db.add(models.Department(name=d_name))
    db.commit()
    print("✅ Departmanlar oluşturuldu.")

    # 2. Patron Kontrolü
    existing_user = db.query(models.User).filter(models.User.email == "patron@gov.tr").first()
    if existing_user:
        print("✅ Patron zaten var.")
        return

    # 3. Patron Kullanıcısı
    patron_user = models.User(
        email="patron@gov.tr",
        password_hash=get_password_hash("123456"),
        role="admin",
        is_active=True
    )
    db.add(patron_user)
    db.commit()
    db.refresh(patron_user)

    # 4. Patron Çalışan Kartı
    patron_employee = models.Employee(
        user_id=patron_user.id,
        first_name="Süper",
        last_name="Patron",
        department_id=4, # Yönetim
        gender="Erkek",
        role="Yönetici",
        salary=200000,
        annual_leave_entitlement=30,
        team_id=None
    )
    db.add(patron_employee)
    db.commit()

    print("✅ Patron başarıyla oluşturuldu! (patron@gov.tr / 123456)")

if __name__ == "__main__":
    init()