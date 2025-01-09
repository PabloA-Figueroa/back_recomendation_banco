from datetime import date
from typing import List, Optional
from pydantic import BaseModel

# Modelos Relacionados
class AcademicInfo(BaseModel):
    area_de_estudio: Optional[str] = None
    area_de_estudio_ponderacion: Optional[int] = None
    nivel_de_estudio: Optional[str] = None
    nivel_de_estudio_ponderacion: Optional[int] = None
    estado_de_estudio: Optional[str] = None
    estado_de_estudio_ponderacion: Optional[int] = None

    class Config:
        orm_mode = True

class LanguageSkill(BaseModel):
    idioma: Optional[str] = None
    idioma_ponderacion: Optional[int] = None
    nivel_escritura: Optional[str] = None
    nivel_escritura_ponderacion: Optional[int] = None
    nivel_habla: Optional[str] = None
    nivel_habla_ponderacion: Optional[int] = None

    class Config:
        orm_mode = True

class WorkExperience(BaseModel):
    nombre_del_puesto: Optional[str] = None
    jerarquia: Optional[str] = None
    # Agrega otros campos según corresponda

    class Config:
        orm_mode = True

class Skills(BaseModel):
    habilidades_blandas: Optional[str] = None
    habilidades_tecnicas: Optional[str] = None
    habilidades_blandas_ponderacion: Optional[int] = None
    habilidades_tecnicas_ponderacion: Optional[int] = None

    class Config:
        orm_mode = True
# Modelo de Datos Pydantic con Ponderaciones
class PersonalInfo(BaseModel):
    class Config:
        from_attributes = True  # Enables ORM mode
        orm_mode = True
        json_encoders = {
            date: lambda v: v.strftime("%Y-%m-%d")
        }
    
    id: int
    nombre_completo: str
    numero_cedula: str
    telefono: str
    correo: str
    linkedin: Optional[str] = None
    estado_civil: Optional[str] = None
    fecha_nacimiento: date
    edad: int
    aspiracion_salarial: float
    tipo_sangre: Optional[str] = None
    direccion: Optional[str] = None
    personal_map_document: Optional[str] = None
    profile_data_id: int

class ProfileData(BaseModel):
    id: Optional[int] = None
    informacion_academica: Optional[AcademicInfo] = None
    informacion_academica_ponderacion: Optional[int] = None
    idioma: Optional[LanguageSkill] = None
    idioma_ponderacion: Optional[int] = None
    experiencia_laboral:  Optional[WorkExperience] = None
    experiencia_laboral_ponderacion: Optional[int] = None
    habilidades: Optional[Skills] = None
    habilidades_ponderacion: Optional[int] = None
    personal_info: Optional[PersonalInfo] = None
    tags: List["ProfileModelTags"] = []

    class Config:
        from_attributes = True
        orm_mode = True


class ProfileModelTags(BaseModel):
    id: int
    tag: str
    profile_data_id: int

    class Config:
        orm_mode = True

# Modelo principal
class ProfileModel(BaseModel):
    personal_map_data: ProfileData

    class Config:
        orm_mode = True
    @classmethod
    def from_orm(cls, orm_object):
        """Convierte un objeto ORM de ProfileModel a un objeto Pydantic ProfileModel."""
        # Primero, convierte la información básica de ProfileModel
        profile_model_data = {
            "personal_map_data": ProfileData.from_orm(orm_object) if orm_object else None
        }
        return cls(**profile_model_data)