from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import os

from app.services.mongodb import MongoConnection


router = FastAPI()
# Ruta fija donde se almacenará el archivo subido
PDF_STORAGE_PATH = r"C:\Users\salas\back_recomendation_banco\data\pdfs\personal_map.pdf"

# Mapeo de claves actuales a nombres descriptivos
KEY_MAPPING = {
    "Texto3": "cedula",
    "Texto4": "telefono",
    "Texto5": "linkedin",
    "Texto7": "estado_civil",
    "Texto8": "nivel_academico",
    "Texto9": "fecha_nacimiento",
    "Texto6": "email",
    "Texto10": "edad",
    "Texto11": "salario",
    "Texto12": "tipo_sangre",
    "Texto2": "nombre_completo",
    "Text15": "direccion_principal",    
    "Texto16": "direccion_secundaria",
    "Texto19": "relacion1",
    "Texto20": "relacion2",
    "Texto21": "relacion3",
    "Texto22": "nombre_relacion1",
    "Texto23": "nombre_relacion2",
    "Texto24": "nombre_relacion3",
    "Texto25": "edad_relacion1",
    "Texto26": "edad_relacion2",
    "Texto27": "edad_relacion3",
    "Texto28": "ocupacion_relacion1",
    "Texto29": "ocupacion_relacion2",
    "Texto30": "ocupacion_relacion3",
    "Texto31": "telefono_relacion1",
    "Texto32": "telefono_relacion2",
    "Texto33": "telefono_relacion3",
    "Texto34": "institucion_estudios",
    "Texto36": "estado_estudios",
    "Texto64": "curso1",
    "Texto65": "progreso_curso1",
    "Texto66": "curso2",
    "Texto67": "progreso_curso2",
    "Texto68": "curso3",
    "Texto69": "progreso_curso3",
    "Texto70": "descripcion_intereses",
    "Texto71": "descripcion_tiempo_libre",
    "Texto72": "objetivo_profesional1",
    "Texto73": "objetivo_profesional2",
    "Texto74": "contribuciones_laborales",
    "Texto75": "firma",
    "Texto76": "fecha_firma",
}

def extract_pdf(file_path: str):
    """Extrae los campos de formulario de un PDF y renombra las claves."""
    try:
        reader = PdfReader(file_path)
        fields = reader.get_form_text_fields()

        # Renombrar las claves usando el mapeo
        renamed_fields = {
            KEY_MAPPING.get(key, key): value for key, value in fields.items()
        }
        
        return renamed_fields
    
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        raise HTTPException(status_code=500, detail="Error procesando el PDF")
    

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    connection = MongoConnection()
    """Endpoint para subir y procesar un PDF."""
    try:
        # Guardar el archivo subido en el sistema
        with open(PDF_STORAGE_PATH, "wb") as f:
            f.write(await file.read())

        # Extraer los datos del PDF
        extracted_data = extract_pdf(PDF_STORAGE_PATH)

        # Guardar los datos en MongoDB
        connection.save_to_mongodb(extracted_data)

        return JSONResponse(
            content={"message": "PDF procesado y datos guardados correctamente.", "data": extracted_data},
            status_code=200,
        )
    except Exception as e:
        print(f"Error procesando el PDF: {e}")
        raise HTTPException(status_code=500, detail="Error procesando el archivo")
