from typing import List, Optional
from pydantic import BaseModel

# Modelo de Datos Pydantic con Ponderaciones
class AcademicInfo(BaseModel):
    area_de_estudio: Optional[str] = None
    area_de_estudio_ponderacion: int = None
    nivel_de_estudio: Optional[str] = None
    nivel_de_estudio_ponderacion: int = None
    estado_de_estudio: Optional[str] = None
    estado_de_estudio_ponderacion: int = None

class LanguageSkill(BaseModel):
    idioma: Optional[str] = None
    idioma_ponderacion: int = None
    nivel_escritura: Optional[str] = None
    nivel_escritura_ponderacion: int = None
    nivel_habla: Optional[str] = None
    nivel_habla_ponderacion: int = None

class WorkExperience(BaseModel):
    nombre_del_puesto: Optional[str] = None
    nombre_del_puesto_ponderacion: int = None
    jerarquia: Optional[str] = None
    jerarquia_ponderacion: int = None
    nombre_de_la_empresa: Optional[str] = None
    nombre_de_la_empresa_ponderacion: int = None
    ubicacion_de_la_empresa: Optional[str] = None
    ubicacion_de_la_empresa_ponderacion: int = None
    tipo_de_empresa: Optional[str] = None
    tipo_de_empresa_ponderacion: int = None
    area_de_trabajo: Optional[str] = None
    area_de_trabajo_ponderacion: int = None
    actualmente_trabajo_aqui: Optional[str] = None
    actualmente_trabajo_aqui_ponderacion: int = None
    tiempo_de_trabajo: Optional[str] = None
    tiempo_de_trabajo_ponderacion: int = None


class Skills(BaseModel):
    habilidades_blandas: Optional[List[dict]] = None
    habilidades_tecnicas: Optional[List[dict]] = None
    habilidades_blandas_ponderacion: int = None
    habilidades_tecnicas_ponderacion: int = None

class ProfileData(BaseModel):
    informacion_academica: Optional[AcademicInfo] = None
    informacion_academica_ponderacion: int = None
    idioma: Optional[LanguageSkill] = None
    idioma_ponderacion: int = None
    experiencia_laboral:  Optional[WorkExperience] = None
    experiencia_laboral_ponderacion: int = None
    habilidades: Optional[Skills] = None
    habilidades_ponderacion: int = None

# Modelo principal
class ProfileModel(BaseModel):
    personal_map_data: Optional[ProfileData] = None