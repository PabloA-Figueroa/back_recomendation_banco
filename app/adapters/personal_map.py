# -*- coding: utf-8 -*-
import json
import os
from http.client import HTTPException
from fastapi import  APIRouter, Depends, UploadFile,File
from app.models.personal_map import  ProfileModel
from app.models.personal_map_mongo import ProfileData, ProfileDataActualizado
from app.services.Extract_pdfs import extract_pdf
from app.services.generate_profile import ejecutar, generar
from app.services.mongodb import MongoConnection, save_to_mongodb

from bson import ObjectId

from pymongo import MongoClient

from typing import List

from fastapi.responses import JSONResponse

PDF_STORAGE_DIR = r"C:\Users\salas\back_recomendation_banco\data\pdfs"

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "pdf_data"
COLLECTION_NAME = "extracted_info"

# Initialize MongoDB Client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

router = APIRouter()

@router.get("/extracts_pdf")
async def extracts_pdf():
    ruta_pdf = r"C:\Users\salas\back_recomendation_banco\data\pdfs\personal_map.pdf"
    if not os.path.exists(ruta_pdf):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    data = extract_pdf(ruta_pdf)    
    return {
        'status': 200,
        'data': data
    }

@router.post("/extract_and_save_multiple_pdfs")
async def extract_and_save_multiple_pdfs(files: List[UploadFile] = File(...)):
    """Endpoint to upload and process multiple PDFs."""
    if not os.path.exists(PDF_STORAGE_DIR):
        os.makedirs(PDF_STORAGE_DIR)

    processed_data = []

    for file in files:
        file_path = os.path.join(PDF_STORAGE_DIR, file.filename)

        try:
            # Save the file locally
            with open(file_path, "wb") as f:
                f.write(await file.read())

            # Extract data from the PDF
            extracted_data = extract_pdf(file_path)

            # Save extracted data to MongoDB
            saved_data = collection.insert_one({
                "filename": file.filename,
                "data": extracted_data
            })

            # Append the response, including the inserted ID
            processed_data.append({
                "filename": file.filename,
                "data": extracted_data,
                "_id": str(saved_data.inserted_id)  # Convert ObjectId to string
            })
        except Exception as e:
            processed_data.append({
                "filename": file.filename,
                "error": str(e)
            })
        finally:
            # Remove the file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

    return JSONResponse(
        content={"message": "Processing completed.", "results": processed_data},
        status_code=200
    )


@router.post("/save_pdf_data")
async def save_pdf_data():
    ruta_pdf = r"C:\Users\salas\back_recomendation_banco\data\pdfs\personal_map.pdf"
    
    if not os.path.exists(ruta_pdf):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        # Extraer datos del PDF
        data = extract_pdf(ruta_pdf)
        
        # Guardar datos en MongoDB
        result = save_to_mongodb(data)
        
        # Convertir ObjectId a string antes de devolver la respuesta
        response_data = {
            "status": 200,
            "message": "Datos guardados en MongoDB exitosamente",
            "data": data,
            "inserted_id": str(result.inserted_id)  # Convertimos ObjectId a string
        }
        
        return response_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar los datos: {e}")


@router.post("/create_profile/")
async def create_profile(profile: ProfileModel):
    # Aquí puedes procesar el objeto 'profile', como guardarlo en una base de datos
    print(profile)
    return {"message": "Perfil creado con éxito", "profile_data": profile}



@router.get("/generate_profile")
async def generate_profile():
    response = generar()
    conecction = MongoConnection()
    try:
        # Guardar los datos en MongoDB
        inserted_id = conecction.save_to_mongodb_ideal_personal_map(response, "ideal_profile")
        print(f"Datos insertados correctamente con ID: {inserted_id}")
        return {
            "status": 200,
            "message": "Datos insertados correctamente",
            "inserted_id": str(inserted_id)
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# TEST ------------------------ 


@router.post("/profile/update", response_model=ProfileDataActualizado)
async def update_profile(data: ProfileDataActualizado):
    coneccion = MongoConnection()
    try:
        # Guardar los datos en MongoDB
        inserted_id = coneccion.save_to_mongodb_ideal_personal_map(data, "personal_map")
        #inserted_id = save_to_mongo    "_id": "64f1a2b3c1b2c3d4e5f6a7b9",db(data)
        print(f"Datos insertados correctamente con ID: {inserted_id}")
        data.id = inserted_id
        print("data",data)
        print(data.id)
        return {
            "status": 200,
            "message": "Datos insertados correctamente",
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
@router.get("/ideal_profile/get")
async def get_ideal_profile():
    conecction = MongoConnection()
    try:
        # Obtener el perfil ideal de MongoDB
        ideal_profile = conecction.get_ideal_model()
        return {
            "status": 200,
            "message": "Perfil ideal obtenido correctamente",
            "data": ideal_profile
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
@router.get("/ideal_profiles/get")
async def get_ideal_profiles():
    conecction = MongoConnection()
    try:
        # Obtener todos los perfiles ideales de MongoDB
        ideal_profiles = conecction.get_all_ideal_models()
        return {
            "status": 200,
            "message": "Perfiles ideales obtenidos correctamente",
            "data": ideal_profiles
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})