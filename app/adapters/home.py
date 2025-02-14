from typing import List
from fastapi import  APIRouter, HTTPException
from app.models.personal_map import ProfileData
from data.database.mongodb import MongoConnection
from fastapi.responses import FileResponse
import os

from data.database.mysql import MySqlConnection

router = APIRouter()

@router.get("/personal_maps/get")
async def get_personal_maps():
    try:
        db = MongoConnection()
        personal_info = db.get_all_personal_info()
        return {
            "status": "200",
            "data": personal_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/profile/get/{id}")
async def get_personal_info(id: str):
    mongo_conn = MongoConnection()
    personal_info = mongo_conn.get_personal_info_by_id(id)
    if personal_info:
        return {
            "status": 200,
            "data": personal_info
        }
    else:
        return {
            "status": 404,
            "message": "Personal info not found"
        }

@router.get("/personal_map/completos/get")
async def get_profile_data():
    try:
        db = MongoConnection()
        profile_data = db.get_extracted_fields_without_personal_info()
        return profile_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/pdf", name="Obtener PDFs")
async def get_file():
    file_path = "/home/pablof/Documentos/study/data/pdfs/1._Plan_docente_test.pdf"
    # Normalizar la ruta del archivo para diferentes sistemas operativos
    normalized_file_path = os.path.normpath(file_path)
    print("NORMAL",normalized_file_path)
    full_file_path = os.path.join(os.getcwd(), normalized_file_path)
    print("FULL",full_file_path)
    # Verificar si el archivo existe
    if not os.path.exists(full_file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el sistema de archivos")
    # Retornar el archivo PDF
    return FileResponse(path=full_file_path, filename=os.path.basename(full_file_path), media_type='application/pdf')