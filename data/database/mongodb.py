from datetime import date, datetime
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from typing import Dict, List, Optional


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
            
            # Convertir campos datetime.date a datetime.datetime si es necesario
            if "fecha_nacimiento" in data_dict.get("personal_info", {}):
                fecha_nacimiento = data_dict["personal_info"]["fecha_nacimiento"]
                if isinstance(fecha_nacimiento, date):
                    data_dict["personal_info"]["fecha_nacimiento"] = datetime(
                        fecha_nacimiento.year, fecha_nacimiento.month, fecha_nacimiento.day
                    )

            # Insertar el documento en MongoDB
            result = self.db[collection_name].insert_one(data_dict)
            # Convertir ObjectId a string si es necesario
            data_dict["_id"] = str(result.inserted_id)
            
            print(f"Documento insertado con ID: {result.inserted_id}")
            print("Datos guardados correctamente en MongoDB")
            return str(result.inserted_id)
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

    def get_tags(self):
        try:
            tags_cursor = self.db["ideal_profile"].find({}, {"_id": 0, "Tag": 1})
            tags = [doc["Tag"] for doc in tags_cursor]
            print("Tags: ", tags)
            return tags
        except Exception as e:
            print(f"Error al obtener los tags: {e}")
            raise

    def get_profiles_by_tag(self, tag):
        try:
            profiles_cursor = self.db["ideal_profile"].find({"Tag": tag}, {"_id": 0})
            profiles = list(profiles_cursor)
            print(f"Perfiles con Tag '{tag}': ", profiles)
            return profiles
        except Exception as e:
            print(f"Error al obtener perfiles con tag '{tag}': {e}")
            raise

    def get_personal_info(self):
        try:
            personal_info = self.db["extracted_fields"].find_one({}, {"_id": 0, "personal_info": 1})
            print("Personal Info: ", personal_info)
            return personal_info
        except Exception as e:
            print(f"Error al obtener la información personal: {e}")
            raise
        
    def get_all_personal_info(self):
        try:
            # Excluir únicamente el campo 'personal_info.familiares' sin incluir todo 'personal_info'
            personal_info_cursor = self.db["extracted_fields"].find({}, {
                "personal_info.familiares": 0
            })
            
            result = []
            for document in personal_info_cursor:
                personal_info = document.get("personal_info", {})
                personal_info["_id"] = str(document["_id"])  # Convertir ObjectId a string si es necesario
                tag = document.get("Tag", [])  # Obtener el campo 'Tag'
                result.append({
                    "personal_info": personal_info,
                    "Tag": tag
                })

            print("Personal Info y Tags: ", result)
            return result   
        except Exception as e:
            print(f"Error al obtener la información personal: {e}")
            raise

    def get_personal_info_by_id(self, id_str: str):
        try:
            object_id = ObjectId(id_str)
            document = self.db["extracted_fields"].find_one(
                {"_id": object_id},
                {
                    "personal_info.familiares": 0
                }
            )
            
            if document:
                document["_id"] = str(document["_id"])  
                return document
            
            print(f"No se encontró información personal para el ID: {id_str}")
            return None
        except Exception as e:
            print(f"Error al obtener la información personal por ID '{id_str}': {e}")
            raise

    def get_extracted_fields_without_personal_info(self) -> List[Dict]:
        try:
            # Obtener todos los documentos excluyendo el campo 'personal_info'
            documents = self.collection.find({}, {"personal_info": 0})
            result = []
            for document in documents:
                document["_id"] = str(document["_id"])  # Convertir ObjectId a string
                result.append(document)
            
            return result
        except Exception as e:
            print(f"Error al obtener los campos extraídos sin la información personal: {e}")
            raise
    
    def update_candidate(self, candidate_id: str, data: Dict):
        try:
             # Convertir el ID de string a ObjectId
            object_id = ObjectId(candidate_id)
            print(f"Updating candidate with id {object_id} in database")
            
            # Crear una copia del diccionario data para no modificar el original
            data_copy = data.copy()

            # Eliminar el _id del diccionario
            if "_id" in data_copy:
                del data_copy["_id"]


            # Actualizar el documento en MongoDB
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": data_copy}  # Usar la copia sin _id
            )
            print(f"Candidato actualizado: {result.modified_count} documentos modificados")
            return result.modified_count
        except Exception as e:
            print(f"Error al actualizar el candidato con ID {candidate_id} en MongoDB: {e}")
            raise
    
