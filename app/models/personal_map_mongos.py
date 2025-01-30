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

# Clase para manejar valores con nombre y ponderación
class Value(BaseModel):
    name: str
    ponderacion: int

# Clase para manejar subsecciones
class Subseccion(BaseModel):
    name: str
    values: List[Value]
    ponderacion: int

# Clase para manejar secciones
class Seccion(BaseModel):
    name: Optional[str] = None
    Subsecciones: List[Subseccion]
    ponderacion: int
# Clase para manejar la información familiar
class Familiar(BaseModel):
    parentesco: str = ""
    nombre: str = ""
    edad: int = 0
    profesion: str = ""
    telefono: str = ""
# Clase para manejar la información personal
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
 # Información de discapacidad
    tipo_descapacidad: Optional[str] = None
    porcentaje_descapacidad: Optional[float] = None

    # Información Familiar
    familiares: List[Familiar] = []
# Clase principal que representa el modelo completo
class ProfileModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={ObjectId: str},  # Serializar ObjectId a str
    )
    Secciones: List[Seccion]
    Tag: Optional[str] = None
    id: Optional[str] = None
    #personal_info: Optional[PersonalInfo] = None

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte un documento MongoDB a un objeto Pydantic ProfileModel."""
        if data:
            # Convertir las secciones
            secciones = []
            for seccion_data in data.get("Secciones", []):
                subsecciones = []
                for subseccion_data in seccion_data.get("Subsecciones", []):
                    values = [Value(**value) for value in subseccion_data.get("values", [])]
                    subseccion = Subseccion(
                        nombre=subseccion_data.get("nombre", ""),
                        values=values,
                        ponderacion=subseccion_data.get("ponderacion", 0)
                    )
                    subsecciones.append(subseccion)
                seccion = Seccion(
                    Subsecciones=subsecciones,
                    ponderacion=seccion_data.get("ponderacion", 0)
                )
                secciones.append(seccion)

            # Obtener el tag y la información personal
            tag = data.get("Tag")
            personal_info_data = data.get("personal_info", {})
            personal_info = PersonalInfo(**personal_info_data) if personal_info_data else None

            return cls(Secciones=secciones, Tag=tag, personal_info=personal_info)
        return None
    

class ProfileModelFromPersonalMap(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={ObjectId: str},  # Serializar ObjectId a str
    )
    Secciones: List[Seccion]
    Tag: Optional[str] = None
    personal_info: Optional[PersonalInfo] = None

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte un documento MongoDB a un objeto Pydantic ProfileModel."""
        if data:
            # Convertir las secciones
            secciones = []
            for seccion_data in data.get("Secciones", []):
                subsecciones = []
                for subseccion_data in seccion_data.get("Subsecciones", []):
                    values = [Value(**value) for value in subseccion_data.get("values", [])]
                    subseccion = Subseccion(
                        nombre=subseccion_data.get("nombre", ""),
                        values=values,
                        ponderacion=subseccion_data.get("ponderacion", 0)
                    )
                    subsecciones.append(subseccion)
                seccion = Seccion(
                    Subsecciones=subsecciones,
                    ponderacion=seccion_data.get("ponderacion", 0)
                )
                secciones.append(seccion)

            # Obtener el tag y la información personal
            tag = data.get("Tag")
            personal_info_data = data.get("personal_info", {})
            personal_info = PersonalInfo(**personal_info_data) if personal_info_data else None

            return cls(Secciones=secciones, Tag=tag, personal_info=personal_info)
        return None