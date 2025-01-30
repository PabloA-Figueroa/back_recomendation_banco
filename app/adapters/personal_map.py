import os
import re
from datetime import datetime
from http.client import HTTPException
from bson import ObjectId
from fastapi import APIRouter, UploadFile, File
from fastapi.encoders import jsonable_encoder
from app.services.Extract_pdfs import extract_pdf
from data.database.mongodb import MongoConnection
from typing import List
from fastapi.responses import JSONResponse
from app.models.personal_map_mongos import ProfileModel, ProfileModelFromPersonalMap, Seccion, Subseccion, Value, PersonalInfo, Familiar

PDF_STORAGE_DIR = r"C:\Users\salas\back_recomendation_banco\data\pdfs"

router = APIRouter()

# Función para parsear fechas en español
def parse_fecha(fecha_str: str) -> str:
    meses = {
        "enero": "01",
        "febrero": "02",
        "marzo": "03",
        "abril": "04",
        "mayo": "05",
        "junio": "06",
        "julio": "07",
        "agosto": "08",
        "septiembre": "09",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12"
    }
    try:
        partes = fecha_str.lower().split(" de ")
        dia = partes[0].zfill(2)
        mes = meses.get(partes[1], "01")
        año = partes[2]
        return f"{año}-{mes}-{dia}"
    except:
        return "1970-01-01"

# Función para extraer números de cadenas
def extract_number(text: str) -> int:
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0

def extract_float(text: str) -> float:
    match = re.search(r'\d+\.?\d*', text.replace(',', ''))
    return float(match.group()) if match else 0.0

def transform_to_profile_model(extracted_data: dict) -> dict:
    secciones = []
    
    # Información Académica
    info_academica = Seccion(
        name="Información Académica",
        Subsecciones=[
            Subseccion(
                name="Área de estudio",
                values=[Value(name=extracted_data.get("titulo_academico", "") or "", ponderacion=0)],
                ponderacion=0
            ),
            Subseccion(
                name="Nivel de estudio",
                values=[Value(name=extracted_data.get("nivel_estudio", "") or "", ponderacion=0)],
                ponderacion=0
            ),
            Subseccion(
                name="Estado de estudio",
                values=[Value(name=extracted_data.get("estado_estudio", "") or "", ponderacion=0)],
                ponderacion=0
            ),
            # Nivel Bachillerato
            Subseccion(
                name="Nivel Bachillerato",
                values=[
                    Value(name=extracted_data.get("institucion_nivel_bachillerato", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("titulo_nivel_bachillerato", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("estado_nivel_bachillerato", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("ciclo_nivel_bachillerato", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            # Tercer Nivel
            Subseccion(
                name="Tercer Nivel",
                values=[
                    Value(name=extracted_data.get("institucion_tercer_nivel", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("titulo_tercer_nivel", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("estado_tercer_nivel", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("ciclo_tercer_nivel", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            # Cuarto Nivel
            Subseccion(
                name="Cuarto Nivel",
                values=[
                    Value(name=extracted_data.get("institucion_cuarto_nivel", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("titulo_cuarto_nivel", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("estado_cuarto_nivel", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("ciclo_cuarto_nivel", "") or "", ponderacion=0)
                ],
                ponderacion=0
            )
        ],
        ponderacion=9
    )
    secciones.append(info_academica)
    
    # Experience Laboral
    experiencia = Seccion(
        name="Experience Laboral",
        Subsecciones=[
            Subseccion(
                name="Nombre del puesto",
                values=[Value(name=extracted_data.get("cargo_actual_trabajo", "") or "", ponderacion=0)],
                ponderacion=0
            ),
            Subseccion(
                name="Jerarquía",
                values=[Value(name=extracted_data.get("jerarquia", "") or "", ponderacion=0)],
                ponderacion=0
            )
        ],
        ponderacion=7
    )
    secciones.append(experiencia)
    
    # Habilidades
    habilidades = Seccion(
        name="Habilidades",
        Subsecciones=[
            Subseccion(
                name="Habilidades blandas",
                values=[
                    Value(name=extracted_data.get("habilidad_blanda1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("habilidad_blanda2", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Habilidades técnicas",
                values=[
                    Value(name=extracted_data.get("habilidad_tecnica1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("habilidad_tecnica2", "") or "", ponderacion=0)
                ],
                ponderacion=9
            )
        ],
        ponderacion=9
    )
    secciones.append(habilidades)
    
    # Información Personal
    fecha_nacimiento = parse_fecha(extracted_data.get("fecha_nacimiento", "1970-01-01"))
    edad = extract_number(extracted_data.get("edad", "0"))
    aspiracion_salarial = extract_float(extracted_data.get("salario", "$0"))
    
    # Información de Discapacidad (si aplica)
    tipo_descapacidad = extracted_data.get("tipo_descapacidad")
    porcentaje_descapacidad = extract_float(extracted_data.get("porcentaje_descapacidad")) if extracted_data.get("porcentaje_descapacidad") else None
    
    # Información Familiar
    familiares = []
    for i in range(1, 4):
        parentesco_key = f"parentesco{i}"
        nombre_key = f"nombre_parentesco{i}"
        edad_key = f"edad_parentesco{i}"
        profesion_key = f"profesion_parentesco{i}"
        telefono_key = f"telefono_parentesco{i}"
        
        parentesco = extracted_data.get(parentesco_key)
        nombre = extracted_data.get(nombre_key)
        edad_familiar = extract_number(extracted_data.get(edad_key, "0"))
        profesion = extracted_data.get(profesion_key)
        telefono = extracted_data.get(telefono_key)
        
        if parentesco and nombre:
            familiar = Familiar(
                parentesco=parentesco or "",
                nombre=nombre or "",
                edad=edad_familiar,
                profesion=profesion or "",
                telefono=telefono or ""
            )
            familiares.append(familiar)
    
    personal_info = PersonalInfo(
        nombre_completo=extracted_data.get("nombre_completo", "") or "",
        numero_cedula=extracted_data.get("cedula", "") or "",
        telefono=extracted_data.get("telefono", "") or "",
        correo=extracted_data.get("email", "") or "",
        linkedin=extracted_data.get("linkedin", "") or None,
        estado_civil=extracted_data.get("estado_civil", "") or None,
        fecha_nacimiento=fecha_nacimiento,
        edad=edad,
        aspiracion_salarial=aspiracion_salarial,
        tipo_sangre=extracted_data.get("tipo_sangre", "") or None,
        direccion=f"{extracted_data.get('direccion_barrio', '')}, {extracted_data.get('direccion_calles', '')}" or None,
        personal_map_document=extracted_data.get("personal_map_document", "") or None,
        tipo_descapacidad=tipo_descapacidad or None,
        porcentaje_descapacidad=porcentaje_descapacidad,
        familiares=[familiar.dict() for familiar in familiares] if familiares else []
    )
    
    # Cursos y Conocimientos
    cursos = Seccion(
        name="Cursos y Conocimientos",
        Subsecciones=[
            Subseccion(
                name="Cursos",
                values=[
                    Value(name=extracted_data.get("curso1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("curso2", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("curso3", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Conocimientos",
                values=[
                    Value(name=extracted_data.get("conocimiento_curso1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("conocimiento_curso2", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("conocimiento_curso3", "") or "", ponderacion=0)
                ],
                ponderacion=0
            )
        ],
        ponderacion=5
    )
    secciones.append(cursos)
    
    # Aficiones y Objetivos Personales
    aficiones = Seccion(
        name="Aficiones y Objetivos Personales",
        Subsecciones=[
            Subseccion(
                name="Aficiones",
                values=[
                    Value(name=extracted_data.get("descripcion_aficiones1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("descripcion_aficiones2", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Objetivos Personales",
                values=[
                    Value(name=extracted_data.get("objetivo_personales1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("objetivo_personales2", "") or "", ponderacion=0)
                ],
                ponderacion=0
            )
        ],
        ponderacion=5
    )
    secciones.append(aficiones)
    
    # Referencias y Observaciones
    referencias = Seccion(
        name="Referencias y Observaciones",
        Subsecciones=[
            Subseccion(
                name="Referencias Institución",
                values=[
                    Value(name=extracted_data.get("referencia_institucion1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("referencia_institucion2", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Referencias Observaciones",
                values=[
                    Value(name=extracted_data.get("referencia_observaciones1", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("referencia_observaciones2", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Elaborado Por",
                values=[
                    Value(name=extracted_data.get("referencia_elabarado_por", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("referencia_fecha", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Observaciones",
                values=[
                    Value(name=extracted_data.get("observaciones_descripcion", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("observaciones_elaborado_por", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("observaciones_fecha", "") or "", ponderacion=0)
                ],
                ponderacion=0
            ),
            Subseccion(
                name="Revisado Por",
                values=[
                    Value(name=extracted_data.get("revisado_por", "") or "", ponderacion=0)
                ],
                ponderacion=0
            )
        ],
        ponderacion=5
    )
    secciones.append(referencias)
    
    # Otros Campos
    otros = Seccion(
        name="Otros",
        Subsecciones=[
            Subseccion(
                name="Contratación Banco",
                values=[Value(name=extracted_data.get("contratacion_banco", "") or "", ponderacion=0)],
                ponderacion=0
            ),
            Subseccion(
                name="Firma",
                values=[
                    Value(name=extracted_data.get("nombre_firma", "") or "", ponderacion=0),
                    Value(name=extracted_data.get("fecha_firma", "") or "", ponderacion=0)
                ],
                ponderacion=0
            )
        ],
        ponderacion=5
    )
    secciones.append(otros)
    
    profile = ProfileModelFromPersonalMap(
        Secciones=[section.dict() for section in secciones],
        Tag="Desarrollo de Software",
        personal_info=personal_info.dict() if personal_info else None
    )
    
    return profile.dict()

@router.get("/extracts_pdf")
async def extracts_pdf():
    ruta_pdf = r"data/pdfs/personal_map.pdf"
    if not os.path.exists(ruta_pdf):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    data = extract_pdf(ruta_pdf)    
    return {
        'status': 200,
        'data': data
    }
def convert_objectid_to_str(data):
    """
    Función recursiva para convertir ObjectId a str en estructuras anidadas.
    """
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)  # Convertir ObjectId a str
    else:
        return data

@router.post("/extract_and_save_multiple_pdfs")
async def extract_and_save_multiple_pdfs(files: List[UploadFile] = File(...)):
    connection = MongoConnection()
    if not os.path.exists(PDF_STORAGE_DIR):
        os.makedirs(PDF_STORAGE_DIR)

    processed_data = []

    for file in files:
        file_path = os.path.join(PDF_STORAGE_DIR, file.filename)

        try:
            with open(file_path, "wb") as f:
                f.write(await file.read())

            extracted_data = extract_pdf(file_path)
            transformed_data = transform_to_profile_model(extracted_data)

            # Convertir a un formato serializable
            transformed_data_serialized = jsonable_encoder(transformed_data)

            # Guardar en MongoDB
            saved_data = connection.collection.insert_one(transformed_data_serialized)

            # Convertir ObjectId a str en la respuesta
            processed_data.append({
                "filename": file.filename,
                "data": transformed_data_serialized,
                "_id": str(saved_data.inserted_id)  # Convertir ObjectId a str
            })
        except Exception as e:
            processed_data.append({
                "filename": file.filename,
                "error": str(e)
            })
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    # Asegurarse de que no haya ObjectId en processed_data
    processed_data_converted = convert_objectid_to_str(processed_data)

    # Serializar a JSON
    processed_data_serialized = jsonable_encoder(processed_data_converted)

    return JSONResponse(
        content={"message": "Processing completed.", "results": processed_data_serialized},
        status_code=200
    )

@router.post("/profile/save")
async def save_profile(data: ProfileModel):
    connection = MongoConnection()
    try:
        # Convertir a un formato serializable
        data_serialized = jsonable_encoder(data)

        # Guardar en MongoDB
        inserted_id = connection.save_to_mongodb_ideal_personal_map(data_serialized, "extracted_fields")

        print(f"Datos insertados correctamente con ID: {inserted_id}")
        #data.id = inserted_id
        return {
            "status": 200,
            "message": "Datos insertados correctamente",
            "id": inserted_id
        }
    except Exception as e:
        return JSONResponse(
            content={"detail": str(e)},
            status_code=500
        )
    