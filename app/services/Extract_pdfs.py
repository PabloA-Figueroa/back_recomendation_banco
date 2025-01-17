from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import os
from typing import List

router = FastAPI()
# Ruta fija donde se almacenará el archivo subido
PDF_STORAGE_PATH = r"C:\Users\salas\back_recomendation_banco\data\pdfs\personal_map.pdf"

# Mapeo de claves actuales a nombres descriptivos
KEY_MAPPING = {

    "Texto3": "cedula",
    "Texto4": "telefono",
    "Texto5": "linkedin",
    "Texto7": "estado_civil",
    "Texto8": "titulo_academico",
    "Texto9": "fecha_nacimiento",
    "Texto6": "email",
    "Texto10": "edad",
    "Texto11": "salario",
    "Texto12": "tipo_sangre",
    "Texto13": "tipo_descapacidad",
    "Texto14": "porcentaje_descapacidad",
    "Texto2": "nombre_completo",
    "Text15": "direccion_barrio",    
    "Texto16": "direccion_calles",
    "Texto17": "nombre_familiar_banco",
    "Texto18": "parentesco_familiar_banco",

    "Texto19": "parentesco1",
    "Texto20": "parentesco2",
    "Texto21": "parentesco3",
    "Texto22": "nombre_parentesco1",
    "Texto23": "nombre_parentesco2",
    "Texto24": "nombre_parentesco3",
    "Texto25": "edad_parentesco1",
    "Texto26": "edad_parentesco2",
    "Texto27": "edad_parentesco3",
    "Texto28": "profesion_parentesco1",
    "Texto29": "profesion_parentesco2",
    "Texto30": "profesion_parentesco3",
    "Texto31": "telefono_parentesco1",
    "Texto32": "telefono_parentesco2",
    "Texto33": "telefono_parentesco3",

    "Texto34": "institucion_nivel_bachillerato",
    "Texto35": "titulo_nivel_bachillerato",
    "Texto36": "estado_nivel_bachillerato",
    "Texto37": "ciclo_nivel_bachillerato",
    "Texto38": "institucion_tercer_nivel",
    "Texto39": "titulo_tercer_nivel",
    "Texto40": "estado_tercer_nivel",
    "Texto41": "ciclo_tercer_nivel",
    "Texto42": "institucion_cuarto_nivel",
    "Texto43": "titulo_cuarto_nivel",
    "Texto44": "estado_cuarto_nivel",
    "Texto45": "ciclo_cuarto_nivel",

    "Texto46": "empresa_actual_trabajo",
    "Texto47": "cargo_actual_trabajo",
    "Texto48": "tiempo_actual_trabajo",
    "Texto49": "motivo_actual_trabajo",
    "Texto50": "jefe_actual_trabajo",
    "Texto51": "telefono_actual_trabajo",
    "Texto52": "empresa_ultimo_trabajo",
    "Texto53": "cargo_ultimo_trabajo",
    "Texto54": "tiempo_ultimo_trabajo",
    "Texto55": "motivo_ultimo_trabajo",
    "Texto56": "jefe_ultimo_trabajo",
    "Texto57": "telefono_ultimo_trabajo",
    "Texto58": "empresa_penultimo_trabajo",
    "Texto59": "cargo_penultimo_trabajo",
    "Texto60": "tiempo_penultimo_trabajo",
    "Texto61": "motivo_penultimo_trabajo",
    "Texto62": "jefe_penultimo_trabajo",
    "Texto63": "telefono_penultimo_trabajo",

    "Texto64": "curso1",
    "Texto65": "conocimiento_curso1",
    "Texto66": "curso2",
    "Texto67": "conocimiento_curso2",
    "Texto68": "curso3",
    "Texto69": "conocimiento_curso3",

    "Texto70": "descripcion_aficiones1",
    "Texto71": "descripcion_aficiones2",

    "Texto72": "objetivo_personales1",
    "Texto73": "objetivo_personales2",

    "Texto74": "contratacion_banco",

    "Texto75": "nombre_firma",
    "Texto76": "fecha_firma",

    "Texto77": "referencia_institucion1",
    "Texto78": "referencia_institucion2",
    "Texto79": "referencia_observaciones1",
    "Texto80": "referencia_observaciones2",

    "Texto83": "referencia_elabarado_por",
    "Texto85": "referencia_fecha",

    "Texto94": "observaciones_descripcion",
    "Texto95": "observaciones_elaborado_por",
    "Texto96": "observaciones_fecha",
    
    "Texto97": "revisado_por",
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
    
