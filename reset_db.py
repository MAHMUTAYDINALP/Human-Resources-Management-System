from app.db.database import engine, Base
from app.db import models
from sqlalchemy import text

def reset_database():
    print("🗑️ Veritabanı temizleniyor (Zorla Silme Modu)...")
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # Tüm tabloları sırasıyla uçuruyoruz 🧨
            connection.execute(text("DROP TABLE IF EXISTS announcements CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS leaves CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS employees CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS teams CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            
            # Referans tabloları da silelim
            connection.execute(text("DROP TABLE IF EXISTS departments CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS employment_types CASCADE;"))
            
            trans.commit()
            print("✅ Tablolar başarıyla silindi.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Hata: {e}")

    print("🏗️ Yeni tablolar oluşturuluyor...")
    Base.metadata.create_all(bind=engine)
    print("🚀 Veritabanı sıfırlandı!")

if __name__ == "__main__":
    reset_database()