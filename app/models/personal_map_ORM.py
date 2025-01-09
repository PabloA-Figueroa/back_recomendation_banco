from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class ProfileDataORM(Base):
    __tablename__ = "profile_data"

    id = Column(Integer, primary_key=True, index=True)
    informacion_academica_ponderacion = Column(Integer, nullable=False)
    idioma_ponderacion = Column(Integer, nullable=False)
    experiencia_laboral_ponderacion = Column(Integer, nullable=False)
    habilidades_ponderacion = Column(Integer, nullable=False)

    # Relaciones con otras tablas
    personal_info = relationship("PersonalInfoORM", back_populates="profile_data", uselist=False, cascade="all, delete-orphan")
    informacion_academica = relationship("AcademicInfoORM", back_populates="profile_data", uselist=False, cascade="all, delete-orphan")
    idioma = relationship("LanguageSkillORM", back_populates="profile_data", uselist=False, cascade="all, delete-orphan")
    experiencia_laboral = relationship("WorkExperienceORM", back_populates="profile_data", uselist=False, cascade="all, delete-orphan")
    habilidades = relationship("SkillsORM", back_populates="profile_data", uselist=False, cascade="all, delete-orphan")
    tags = relationship("ProfileModelTagsORM", back_populates="profile_data", cascade="all, delete-orphan")

class PersonalInfoORM(Base):
    __tablename__ = "personal_info"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(100), nullable=False)
    numero_cedula = Column(String(50), nullable=False)
    telefono = Column(String(20), nullable=False)
    correo = Column(String(100), nullable=False)
    linkedin = Column(String(100), nullable=True)
    estado_civil = Column(String(50), nullable=True)
    fecha_nacimiento = Column(Date, nullable=False)
    edad = Column(Integer, nullable=False)
    aspiracion_salarial = Column(Float, nullable=False)
    tipo_sangre = Column(String(10), nullable=True)
    direccion = Column(String(255), nullable=True)
    personal_map_document = Column(String(255), nullable=True)

    profile_data_id = Column(Integer, ForeignKey('profile_data.id'), nullable=False)
    profile_data = relationship("ProfileDataORM", back_populates="personal_info")

class AcademicInfoORM(Base):
    __tablename__ = "academic_info"

    id = Column(Integer, primary_key=True, index=True)
    area_de_estudio = Column(String(100), nullable=False)
    area_de_estudio_ponderacion = Column(Integer, nullable=False)
    nivel_de_estudio = Column(String(100), nullable=False)
    nivel_de_estudio_ponderacion = Column(Integer, nullable=False)
    estado_de_estudio = Column(String(100), nullable=False)
    estado_de_estudio_ponderacion = Column(Integer, nullable=False)

    profile_data_id = Column(Integer, ForeignKey('profile_data.id'), nullable=False)
    profile_data = relationship("ProfileDataORM", back_populates="informacion_academica")

class LanguageSkillORM(Base):
    __tablename__ = "language_skill"

    id = Column(Integer, primary_key=True, index=True)
    idioma = Column(String(50), nullable=False)
    idioma_ponderacion = Column(Integer, nullable=False)
    nivel_escritura = Column(String(50), nullable=False)
    nivel_escritura_ponderacion = Column(Integer, nullable=False)
    nivel_habla = Column(String(50), nullable=False)
    nivel_habla_ponderacion = Column(Integer, nullable=False)

    profile_data_id = Column(Integer, ForeignKey('profile_data.id'), nullable=False)
    profile_data = relationship("ProfileDataORM", back_populates="idioma")

class EmpresaORM(Base):
    __tablename__ = "empresa"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)

    experiencias_laborales = relationship("WorkExperienceORM", back_populates="empresa")

class WorkExperienceORM(Base):
    __tablename__ = "work_experience"

    id = Column(Integer, primary_key=True, index=True)
    nombre_del_puesto = Column(String(100), nullable=False)
    jerarquia = Column(String(50), nullable=False)

    empresa_id = Column(Integer, ForeignKey('empresa.id'), nullable=False)
    empresa = relationship("EmpresaORM", back_populates="experiencias_laborales")

    profile_data_id = Column(Integer, ForeignKey('profile_data.id'), nullable=False)
    profile_data = relationship("ProfileDataORM", back_populates="experiencia_laboral")

class SkillsORM(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    habilidades_blandas = Column(Text, nullable=False)
    habilidades_tecnicas = Column(Text, nullable=False)
    habilidades_blandas_ponderacion = Column(Integer, nullable=False)
    habilidades_tecnicas_ponderacion = Column(Integer, nullable=False)

    profile_data_id = Column(Integer, ForeignKey('profile_data.id'), nullable=False)
    profile_data = relationship("ProfileDataORM", back_populates="habilidades")

class ProfileModelTagsORM(Base):
    __tablename__ = "profile_model_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(50), nullable=False)

    profile_data_id = Column(Integer, ForeignKey('profile_data.id'), nullable=False)
    profile_data = relationship("ProfileDataORM", back_populates="tags")