from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

# 1. KULLANICI TABLOSU (Giriş Bilgileri Burada)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="employee") # admin, hr, employee
    is_active = Column(Boolean, default=True)

    # İlişki: Bir kullanıcının bir personel kartı olur
    employee = relationship("Employee", back_populates="user", uselist=False, cascade="all, delete-orphan")


# 2. PERSONEL TABLOSU (Maaş, İzin vb. Burada)
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    employment_type_id = Column(Integer, ForeignKey("employment_types.id"))
    gender = Column(String)
    birth_date = Column(Date, nullable=True)
    role = Column(String) # İşçi, Mühendis, Müdür vb.
    salary = Column(Integer, default=17002)
    
    # İZİN HAKLARI
    annual_leave_entitlement = Column(Integer, default=14)
    excuse_leave_entitlement = Column(Integer, default=7)
    sick_leave_entitlement = Column(Integer, default=30)
    
    # Takım İlişkisi
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # İlişkiler
    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees")
    employment_type = relationship("EmploymentType", back_populates="employees")
    leaves = relationship("Leave", back_populates="employee")
    announcements = relationship("Announcement", back_populates="author")
    
    # Takım ilişkileri
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    managed_teams = relationship("Team", back_populates="leader", foreign_keys="Team.leader_id")

    # 👇 İŞTE EKSİK OLAN SİHİRLİ PARÇA BURASI! ✅
    # Bu kod, "Employee" nesnesine "email" sorulduğunda gidip "User"dan almasını sağlar.
    @property
    def email(self):
        return self.user.email if self.user else None


# 3. DİĞER TABLOLAR (Buralara dokunmadık, olduğu gibi kalsın)
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    employees = relationship("Employee", back_populates="department")

class EmploymentType(Base):
    __tablename__ = "employment_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    employees = relationship("Employee", back_populates="employment_type")

class LeaveType(Base):
    __tablename__ = "leave_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    leaves = relationship("Leave", back_populates="leave_type")

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    reason = Column(String)
    status = Column(String, default="Beklemede") # Beklemede, Onaylandı, Reddedildi
    
    employee = relationship("Employee", back_populates="leaves")
    leave_type = relationship("LeaveType", back_populates="leaves")

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("employees.id"))
    
    # Yeni Özellikler: Hedef Kitle
    is_public = Column(Boolean, default=False)  # Herkese açık mı?
    target_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True) # Belirli bir takıma mı?

    author = relationship("Employee", back_populates="announcements")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    leader_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    leader = relationship("Employee", back_populates="managed_teams", foreign_keys=[leader_id])
    members = relationship("Employee", back_populates="team", foreign_keys="Employee.team_id")