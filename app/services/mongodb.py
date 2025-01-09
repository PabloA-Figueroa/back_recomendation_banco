from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from typing import Dict


# Configura la conexión con MongoDB
MONGO_URI = "mongodb://localhost:27017"  # Cambia según la configuración de tu base de datos
DB_NAME = "pdfData"
COLLECTION_NAME = "extracted_fields"

# Conexión a MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("Conexión exitosa a MongoDB")
except ServerSelectionTimeoutError as e:
    print(f"Error de conexión a MongoDB: {e}")


    

def save_to_mongodb(data: Dict):
    """
    Guarda los datos extraídos del PDF en la base de datos MongoDB.
    """
    try:
        print(f"Guardando los siguientes datos en MongoDB: {data}")
        result = collection.insert_one(data)
        print(f"Documento insertado con ID: {result.inserted_id}")
        print("Datos guardados correctamente en MongoDB")
    except Exception as e:
        print(f"Error al guardar en MongoDB: {e}")
