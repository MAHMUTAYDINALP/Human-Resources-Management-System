from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine=create_engine(settings.DATABASE_URL)     #postgreSQL'e baglanacak motor


SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)     #her oturum açmada kullanılacak session

Base=declarative_base()

def get_db():
    db=SessionLocal()

    try:
        yield db

    finally:
        db.close()