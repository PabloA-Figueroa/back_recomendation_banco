import os
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, joinedload, noload, contains_eager
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from app.models.personal_map import AcademicInfo, LanguageSkill, PersonalInfo, ProfileData, ProfileModel, ProfileModelTags, Skills, WorkExperience
from app.models.personal_map_ORM import PersonalInfoORM, AcademicInfoORM, LanguageSkillORM, WorkExperienceORM, SkillsORM, ProfileModelTagsORM, ProfileDataORM

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
            profile_data_orm = db.query(ProfileDataORM).filter(ProfileDataORM.id == profile_id).first()
            if profile_data_orm:
                return ProfileModel.from_orm(profile_data_orm)
            return None

    def get_all_profile_models(self):
       """Obtener todos los perfiles de modelo."""
       with self.SessionLocal() as db:
            profile_data_orms = db.query(ProfileDataORM).options(
                joinedload(ProfileDataORM.personal_info).options(noload("*")),
                joinedload(ProfileDataORM.informacion_academica).options(noload("*")),
                joinedload(ProfileDataORM.idioma).options(noload("*")),
                joinedload(ProfileDataORM.experiencia_laboral).options(noload("*")),
                joinedload(ProfileDataORM.habilidades).options(noload("*")),
                joinedload(ProfileDataORM.tags).options(noload("*"))
            ).all()
            return [ProfileModel.from_orm(profile_data_orm) for profile_data_orm in profile_data_orms]

    def get_tags_by_profile_model(self, profile_model_id: int):
        """Obtener todas las etiquetas asociadas a un perfil de modelo."""
        with self.SessionLocal() as db:
            return db.query(ProfileModelTagsORM).filter(
                ProfileModelTagsORM.profile_data_id == profile_model_id
            ).all()
    
    def get_all_ideal_personal_maps(self):
        try:
            with self.SessionLocal() as db:
                # Raw SQL query using text()
                sql_query = text("""
                    SELECT * FROM academic_info
                    JOIN profile_data ON academic_info.profile_data_id = profile_data.id
                    JOIN language_skill ON profile_data.id = language_skill.profile_data_id
                    JOIN skills ON profile_data.id = skills.profile_data_id
                    JOIN work_experience ON profile_data.id = work_experience.profile_data_id
                    JOIN empresa ON work_experience.empresa_id = empresa.id
                """)
                
                result = db.execute(sql_query)
                
                rows = result.fetchall()
                
                profiles = []
                for row in rows:
                    profile = ProfileData(
                        id=row.id,
                        informacion_academica=AcademicInfo(
                            area_de_estudio=row.area_de_estudio,
                            area_de_estudio_ponderacion=row.area_de_estudio_ponderacion,
                            nivel_de_estudio=row.nivel_de_estudio,
                            nivel_de_estudio_ponderacion=row.nivel_de_estudio_ponderacion,
                            estado_de_estudio=row.estado_de_estudio,
                            estado_de_estudio_ponderacion=row.estado_de_estudio_ponderacion
                        ),
                        informacion_academica_ponderacion=row.informacion_academica_ponderacion,
                        idioma=LanguageSkill(
                            idioma=row.idioma,
                            idioma_ponderacion=row.idioma_ponderacion,
                            nivel_escritura=row.nivel_escritura,
                            nivel_escritura_ponderacion=row.nivel_escritura_ponderacion,
                            nivel_habla=row.nivel_habla,
                            nivel_habla_ponderacion=row.nivel_habla_ponderacion
                        ),
                        idioma_ponderacion=row.idioma_ponderacion,
                        experiencia_laboral=WorkExperience(
                            nombre_del_puesto=row.nombre_del_puesto,
                            jerarquia=row.jerarquia
                        ),
                        experiencia_laboral_ponderacion=row.experiencia_laboral_ponderacion,
                        habilidades=Skills(
                            habilidades_blandas=row.habilidades_blandas,
                            habilidades_tecnicas=row.habilidades_tecnicas,
                            habilidades_blandas_ponderacion=row.habilidades_blandas_ponderacion,
                            habilidades_tecnicas_ponderacion=row.habilidades_tecnicas_ponderacion
                        ),
                        habilidades_ponderacion=row.habilidades_ponderacion
                    )
                    profiles.append(profile)
                
                return profiles
                
        except SQLAlchemyError as e:
            raise e
        
    def get_all_candidates(self) -> List[ProfileData]:
        try:
            with self.SessionLocal() as db:
                sql_query = text("""
                    SELECT 
                        ai.area_de_estudio,
                        ai.nivel_de_estudio,
                        ai.estado_de_estudio,
                        ls.idioma,
                        ls.nivel_escritura,
                        ls.nivel_habla,
                        we.nombre_del_puesto,
                        we.jerarquia,
                        sk.habilidades_blandas,
                        sk.habilidades_tecnicas,
                        pd.id
                    FROM academic_info ai
                    JOIN profile_data pd ON ai.profile_data_id = pd.id
                    JOIN language_skill ls ON pd.id = ls.profile_data_id
                    JOIN skills sk ON pd.id = sk.profile_data_id
                    JOIN work_experience we ON pd.id = we.profile_data_id
                    JOIN empresa e ON we.empresa_id = e.id
                """)

                result = db.execute(sql_query)
                rows = result.fetchall()

                profiles = []
                for row in rows:
                    profile = ProfileData(
                    id=row.id,
                    informacion_academica=AcademicInfo(
                        area_de_estudio=row.area_de_estudio,
                        nivel_de_estudio=row.nivel_de_estudio,
                        estado_de_estudio=row.estado_de_estudio
                        ),
                    idioma=LanguageSkill(
                        idioma=row.idioma,
                        nivel_escritura=row.nivel_escritura,
                        nivel_habla=row.nivel_habla
                        ),
                    experiencia_laboral=WorkExperience(
                        nombre_del_puesto=row.nombre_del_puesto,
                        jerarquia=row.jerarquia
                        ),
                    habilidades=Skills(
                        habilidades_blandas=row.habilidades_blandas,
                        habilidades_tecnicas=row.habilidades_tecnicas
                        )
                )
                    profiles.append(profile)
                    
                return profiles

        except SQLAlchemyError as e:
            raise e
        

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
                profile_data_id=item.profile_data_id,
            ) for item in results]