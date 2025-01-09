# -*- coding: utf-8 -*-
import json
import os
from http.client import HTTPException
from fastapi import  APIRouter, Depends
from app.models.personal_map import  ProfileModel
from app.services.Extract_pdfs import extract_pdf
from app.services.generate_profile import ejecutar
from app.services.mongodb import save_to_mongodb


router = APIRouter()

@router.get("/transform_pdf")
async def transform_pdf():
    ruta_pdf = r"C:\Users\salas\back_recomendation_banco\data\pdfs\personal_map.pdf"
    if not os.path.exists(ruta_pdf):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    data = extract_pdf(ruta_pdf)
    return {
        'status': 200,
        'data': data
    }




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
    response = ejecutar()
    return {
        'status': 200,
        'data': response
    }