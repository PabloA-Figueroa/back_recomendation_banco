# -*- coding: utf-8 -*-
import json
import os
from http.client import HTTPException
from fastapi import  APIRouter, Depends
from app.models.personal_map import  ProfileModel
from app.services.ETL_pdfs import extract_personal_map_data
from app.services.generate_profile import ejecutar

router = APIRouter()

@router.get("/transform_pdf")
async def transform_pdf():
    ruta_pdf = r"/home/pablof/PycharmProjects/recomendacionBanco/data/pdfs/personal_map.pdf"
    if not os.path.exists(ruta_pdf):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    data = extract_personal_map_data(ruta_pdf)

    return {
        'status': 200,
        'data': data
    }
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