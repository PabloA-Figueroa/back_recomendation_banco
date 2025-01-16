from datetime import date, datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from typing import Dict


# Configura la conexión con MongoDB
MONGO_URI = "mongodb://localhost:27017"  # Cambia según la configuración de tu base de datos
DB_NAME = "pdfData"
COLLECTION_NAME = "extracted_fields"

class MongoConnection:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("Conexión exitosa a MongoDB", self.collection)
        except ServerSelectionTimeoutError as e:
            print(f"Error de conexión a MongoDB: {e}")

            
    def save_to_mongodb_personal_map(self, data: Dict, collection_name):
        try:
            print(f"Guardando los siguientes datos en MongoDB: {data}")
            data_dict = data.model_dump() if hasattr(data, "model_dump") else data

            # Insertar el documento en MongoDB
            result = self.db[collection_name].insert_one(data_dict)
            print(f"Documento insertado con ID: {result.inserted_id}")
            print("Datos guardados correctamente en MongoDB")
            return {'inserted_id': str(result.inserted_id)}
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")
            raise
# IDEAL PROFILE 
    def save_to_mongodb_ideal_personal_map(self, data: Dict, collection_name):
        try:
            print(f"Guardando los siguientes datos en MongoDB: {data}")
            data_dict = data.model_dump() if hasattr(data, "model_dump") else data

            # Convertir campos datetime.date a datetime.datetime
            if "fecha_nacimiento" in data_dict.get("personal_info", {}):
                fecha_nacimiento = data_dict["personal_info"]["fecha_nacimiento"]
                if isinstance(fecha_nacimiento, date):
                    data_dict["personal_info"]["fecha_nacimiento"] = datetime(
                        fecha_nacimiento.year, fecha_nacimiento.month, fecha_nacimiento.day
                    )

            # Insertar el documento en MongoDB
            result = self.db[collection_name].insert_one(data_dict)
            print(f"Documento insertado con ID: {result.inserted_id}")
            print("Datos guardados correctamente en MongoDB")
            return result.inserted_id
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")
            raise

    def get_ideal_model(self):
        try:
            ideal_profile = self.db["ideal_profile"].find_one({}, {"_id": 0})
            print("Ideal Profile: ", ideal_profile)
            return ideal_profile
        except Exception as e:
            print(f"Error al obtener el perfil ideal: {e}")
            raise

    def get_all_ideal_models(self):
        try:
            # Obtener todos los documentos de la colección "ideal_profile"
            ideal_profile_cursor = self.db["ideal_profile"].find({}, {"_id": 0})
            
            # Convertir el cursor a una lista de documentos
            ideal_profile_list = list(ideal_profile_cursor)
            
            print("Ideal Profile: ", ideal_profile_list)
            return ideal_profile_list
        except Exception as e:
            print(f"Error al obtener el perfil ideal: {e}")
            raise