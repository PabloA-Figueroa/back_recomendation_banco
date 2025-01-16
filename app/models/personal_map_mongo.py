from datetime import date, datetime
import json
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
# Para manejar ObjectId en Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return handler(core_schema.str_schema())


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o) 
        return json.JSONEncoder.default(self, o)
class AcademicInfo(BaseModel):
    area_de_estudio: Optional[str] = None
    area_de_estudio_ponderacion: Optional[int] = None
    nivel_de_estudio: Optional[str] = None
    nivel_de_estudio_ponderacion: Optional[int] = None
    estado_de_estudio: Optional[str] = None
    estado_de_estudio_ponderacion: Optional[int] = None

class LanguageSkill(BaseModel):
    idioma: Optional[str] = None
    idioma_ponderacion: Optional[int] = None
    nivel_escritura: Optional[str] = None
    nivel_escritura_ponderacion: Optional[int] = None
    nivel_habla: Optional[str] = None
    nivel_habla_ponderacion: Optional[int] = None

class WorkExperience(BaseModel):
    nombre_del_puesto: Optional[str] = None
    jerarquia: Optional[str] = None

class Skills(BaseModel):
    habilidades_blandas: Optional[str] = None
    habilidades_tecnicas: Optional[str] = None
    habilidades_blandas_ponderacion: Optional[int] = None
    habilidades_tecnicas_ponderacion: Optional[int] = None

# Modelo de Datos Pydantic con Ponderaciones
class PersonalInfo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,  # Reemplaza allow_population_by_field_name
        json_encoders={date: lambda v: datetime(v.year, v.month, v.day)},  # Convertir date a datetime
                )
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

class ProfileData(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    informacion_academica: Optional[AcademicInfo] = None
    informacion_academica_ponderacion: Optional[int] = None
    idioma: Optional[LanguageSkill] = None
    idioma_ponderacion: Optional[int] = None
    experiencia_laboral: Optional[WorkExperience] = None
    experiencia_laboral_ponderacion: Optional[int] = None
    habilidades: Optional[Skills] = None
    habilidades_ponderacion: Optional[int] = None
    personal_info: Optional[PersonalInfo] = None
    tags: Optional["ProfileModelTags"] = None

class ProfileDataActualizado(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    informacion_academica: Optional[List[AcademicInfo]] = None
    informacion_academica_ponderacion: Optional[int] = None
    experiencia_laboral: Optional[WorkExperience] = None
    experiencia_laboral_ponderacion: Optional[int] = None
    habilidades: Optional[Skills] = None
    habilidades_ponderacion: Optional[int] = None
    personal_info: Optional[PersonalInfo] = None
    tags: List["ProfileModelTags"] = []
class TagModel(BaseModel):
    tag: str
class ProfileIdealMongo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    informacion_academica: Optional[List[AcademicInfo]] = None
    informacion_academica_ponderacion: Optional[int] = None
    experiencia_laboral: Optional[List[WorkExperience]] = None
    experiencia_laboral_ponderacion: Optional[int] = None
    habilidades: Optional[List[Skills]] = None
    habilidades_ponderacion: Optional[int] = None
    tags: Optional[TagModel] = None

class ProfileModelTags(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    tag: str
    profile_data_id: PyObjectId


# Modelo principal
class ProfileModel(BaseModel):
    personal_map_data: ProfileData

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte un documento MongoDB a un objeto Pydantic ProfileModel."""
        if data:
            return cls(personal_map_data=ProfileDataActualizado(**data))
        return None