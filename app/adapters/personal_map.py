# -*- coding: utf-8 -*-
import os
from http.client import HTTPException
from fastapi import  APIRouter, Depends, UploadFile,File
from app.services.Extract_pdfs import extract_pdf
from data.database.mongodb import MongoConnection
from pymongo import MongoClient
from typing import List
from fastapi.responses import JSONResponse

PDF_STORAGE_DIR = r"C:\Users\salas\back_recomendation_banco\data\pdfs"


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
    conecction = MongoConnection()
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
            saved_data = conecction.collection.insert_one({
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
    connection = MongoConnection()
    ruta_pdf = r"C:\Users\salas\back_recomendation_banco\data\pdfs\personal_map.pdf"
    
    if not os.path.exists(ruta_pdf):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        # Extraer datos del PDF
        data = extract_pdf(ruta_pdf)
        
        # Guardar datos en MongoDB
        result = connection.save_to_mongodb(data)
        
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


