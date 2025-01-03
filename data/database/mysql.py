import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from app.models.personal_map import PersonalInfo
from app.models.personal_map_ORM import PersonalInfoORM, AcademicInfoORM, LanguageSkillORM, WorkExperienceORM, SkillsORM, ProfileModelTagsORM, ProfileModelORM, ProfileDataORM

load_dotenv()

DATABASE_URL = (
    f"mysql+mysqlconnector://{os.getenv('USER_MYSQL')}:{os.getenv('PASSWORD_MYSQL')}@"
    f"{os.getenv('IP_SERVER')}/{os.getenv('DATABASE')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MySqlConnection:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        print("Conexión MySQL establecida")

    def get_db(self):
        """Obtener una sesión de base de datos."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_profile_model(self, profile_id: int):
        """Obtener un perfil de modelo por ID."""
        with self.SessionLocal() as db:
            return db.query(ProfileModelORM).filter(ProfileModelORM.id == profile_id).first()

    def get_all_profile_models(self):
        """Obtener todos los perfiles de modelo."""
        with self.SessionLocal() as db:
            return db.query(ProfileModelORM).all()

    def get_profile_data(self, data_id: int):
        """Obtener datos de perfil por ID."""
        with self.SessionLocal() as db:
            return db.query(ProfileDataORM).filter(ProfileDataORM.id == data_id).first()

    def get_academic_info(self, academic_id: int):
        """Obtener información académica por ID."""
        with self.SessionLocal() as db:
            return db.query(AcademicInfoORM).filter(AcademicInfoORM.id == academic_id).first()

    def get_language_skill(self, language_id: int):
        """Obtener habilidad de idioma por ID."""
        with self.SessionLocal() as db:
            return db.query(LanguageSkillORM).filter(LanguageSkillORM.id == language_id).first()

    def get_work_experience(self, work_id: int):
        """Obtener experiencia laboral por ID."""
        with self.SessionLocal() as db:
            return db.query(WorkExperienceORM).filter(WorkExperienceORM.id == work_id).first()

    def get_skills(self, skills_id: int):
        """Obtener habilidades por ID."""
        with self.SessionLocal() as db:
            return db.query(SkillsORM).filter(SkillsORM.id == skills_id).first()

    def get_profile_model_tags(self, tag_id: int):
        """Obtener etiquetas de perfil por ID."""
        with self.SessionLocal() as db:
            return db.query(ProfileModelTagsORM).filter(ProfileModelTagsORM.id == tag_id).first()

    def get_tags_by_profile_model(self, profile_model_id: int):
        """Obtener todas las etiquetas asociadas a un perfil de modelo."""
        with self.SessionLocal() as db:
            return db.query(ProfileModelTagsORM).filter(
                ProfileModelTagsORM.profile_model_id == profile_model_id
            ).all()

    def get_all_personal_info(self):
        """Obtener toda la información personal."""
        with self.SessionLocal() as db:
            results = db.query(PersonalInfoORM).all()
            return [PersonalInfo(
                id=item.id,
                nombre_completo=item.nombre_completo,
                numero_cedula=item.numero_cedula,
                telefono=item.telefono,
                correo=item.correo,
                linkedin=item.linkedin,
                estado_civil=item.estado_civil,
                fecha_nacimiento=item.fecha_nacimiento,
                edad=item.edad,
                aspiracion_salarial=item.aspiracion_salarial,
                tipo_sangre=item.tipo_sangre,
                direccion=item.direccion,
                personal_map_document=item.personal_map_document,
                profile_model_id=item.profile_model_id,
            ) for item in results]