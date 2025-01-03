from fastapi import FastAPI
from app.adapters import personal_map, home
app = FastAPI()

app.include_router(personal_map.router, tags=["Personal Map"], prefix="/personal_map")
app.include_router(home.router, tags=["Home"], prefix="/home")