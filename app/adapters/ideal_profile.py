from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.personal_map import ProfileDataActualizado
from app.models.personal_map_mongos import ProfileModel
from app.services.generate_profile import generar
from data.database.mongodb import MongoConnection
router = APIRouter()

@router.get("/generate_profile")
async def generate_profile(prompt:str):
    response = generar(prompt)
    conecction = MongoConnection()
    try:
        # Guardar los datos en MongoDB
        conecction.save_to_mongodb_ideal_personal_map(response, "ideal_profile")
        #print(f"Datos insertados correctamente con ID: {inserted_id}")
        print(response)
        return {
            "status": 200,
            "message": "Datos insertados correctamente",
            "data": response
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@router.post("/profile/update")
async def update_profile(data: ProfileModel):
    coneccion = MongoConnection()
    try:
        # Guardar los datos en MongoDB
        inserted_id = coneccion.save_to_mongodb_ideal_personal_map(data, "personal_map")
        print(f"Datos insertados correctamente con ID: {inserted_id}")
        #data.id = inserted_id
        return {
            "status": 200,
            "message": "Datos insertados correctamente",
            "id": inserted_id
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
@router.get("/profile/get")
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
    
@router.get("/profiles/get")
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
    
@router.get("/tags/get")
async def get_tags():
    conecction = MongoConnection()
    try:
        # Obtener los tags de los perfiles ideales de MongoDB
        tags = conecction.get_tags()
        return {
            "status": 200,
            "message": "Tags obtenidos correctamente",
            "data": tags
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
@router.get("/profile/tag/{tag}")
async def get_profiles_by_tag(tag: str):
    conecction = MongoConnection()
    try:
        # Obtener los perfiles ideales con el tag especificado de MongoDB
        profiles = conecction.get_profiles_by_tag(tag)
        return {
            "status": 200,
            "message": f"Perfiles con tag '{tag}' obtenidos correctamente",
            "data": profiles
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})