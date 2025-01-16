# -*- coding: utf-8 -*-
import json
import os
from http.client import HTTPException
from fastapi import  APIRouter, UploadFile,File # type: ignore
from app.models.personal_map import  ProfileModel
from app.services.Extract_pdfs import extract_pdf
from app.services.generate_profile import generar
from app.services.mongodb import save_to_mongodb

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




    
@router.post("/create_profile/")
async def create_profile(profile: ProfileModel):
    # Aquí puedes procesar el objeto 'profile', como guardarlo en una base de datos
    print(profile)
    return {"message": "Perfil creado con éxito", "profile_data": profile}


@router.get("/generate_profile")
async def generate_profile():
    response = generar()
    return {
        'status': 200,
        'data': response
    }