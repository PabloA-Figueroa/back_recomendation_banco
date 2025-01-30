from fastapi import APIRouter, HTTPException
from typing import Dict, List

from app.services.recomendacion import generate_recomendation
from pydantic import BaseModel
from typing import List, Optional


# Import necessary models/schemas (assuming they exist)

class ValueModel(BaseModel):
    name: str
    ponderacion: int

class SubseccionModel(BaseModel):
    name: str
    values: List[ValueModel]
    ponderacion: int

class SeccionModel(BaseModel):
    name: str
    Subsecciones: List[SubseccionModel]
    ponderacion: int

class IdealProfile(BaseModel):
    Secciones: List[SeccionModel]
    Tag: str

class CandidateResponse(BaseModel):
    id: Optional[int]
    nombre: Optional[str]
    informacion_academica_ponderacion: Optional[float]
    idioma_ponderacion: Optional[float]
    experiencia_laboral_ponderacion: Optional[float]
    habilidades_ponderacion: Optional[float]

router = APIRouter()


@router.post("/generate")
async def get_recommendation(ideal_profile: IdealProfile) :
    print("\n=== Starting recommendation generation ===")
    try:
        recommendations = generate_recomendation(ideal_profile.dict())
        # Transformar los diccionarios a objetos CandidateResponse
        return {
            "status": "200",
            "message": "Recomendaciones generadas exitosamente",
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))