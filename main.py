from fastapi import FastAPI
from app.adapters import personal_map, home
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Permite solicitudes desde Angular
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)
app.include_router(personal_map.router, tags=["Personal Map"], prefix="/personal_map")
app.include_router(home.router, tags=["Home"], prefix="/home")