import json
from typing import List, Dict
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from app.models.personal_map import ProfileModel, ProfileData
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from app.services.generate_profile import generate_ideal_profile
from data.database.mongodb import MongoConnection

load_dotenv()
print("Environment variables loaded")

# Configuración del modelo
model = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    temperature=1,
    api_key=os.getenv('GEMINI_API_KEY')
)
print(f"Model initialized with temperature={model.temperature}")

def assign_weights_to_candidate(ideal_profile: Dict, candidate: Dict) -> Dict:
    """
    Asigna pesos a las características de un candidato en función del perfil ideal.
    """
    print("\n=== Starting weight assignment for candidate ===")
    print(f"\nProcessing candidate ID: {candidate.get('_id', 'Unknown')}")  # .get() en diccionario    
    parser = JsonOutputParser()
    print("JSON parser initialized")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            Eres un experto en recursos humanos y debes asignar pesos a las características de un candidato en función de un perfil ideal.
            Debes comparar las características del candidato con el perfil ideal y asignar un peso a cada característica del candidato.
            {format_instructions}
            Debes devolver con el mismo formato de entrada, pero con los pesos asignados a las características del candidato en base a el perfil ideal.            
            """),
            ("user", """
            Perfil ideal: {ideal_profile}
            Candidato: {candidate}
            Asigna pesos a las características del candidato en función del perfil ideal.
            Ademas de las ponderaciones, la explicación de por qué se asignó cada peso es importante y deberia ir al final de la respuesta en un campo llamado "explicacion".
            """),
        ]
    )
    print("Prompt template created")
    
    format_instructions = parser.get_format_instructions()
    print("Format instructions retrieved")
    
    chain = prompt | model | parser
    print("Processing chain created")
    
    print("\nInput data:")
    print(f"Ideal profile: {json.dumps(ideal_profile, indent=2)}")
    print(f"Candidate: {json.dumps(candidate, indent=2)}")  

    result = chain.invoke({
        "ideal_profile": json.dumps(ideal_profile),
        "candidate": json.dumps(candidate),  
        "format_instructions": format_instructions
    })
    
    print("\nWeight assignment result:")
    print(json.dumps(result, indent=2))
    print("=== Weight assignment completed ===\n")
    return result

def compare_candidates(ideal_profile: Dict, candidates: List[Dict]) -> List[Dict]:
    """
    Compara las ponderaciones de los candidatos y selecciona los 5 mejores.
    """
    print("\n=== Starting candidate comparison ===")
    print(f"Total candidates to process: {len(candidates)}")
    
    weighted_candidates = []
    for i, candidate in enumerate(candidates, 1):
        print(f"\nProcessing candidate {i}/{len(candidates)}")
        weighted_candidate = assign_weights_to_candidate(ideal_profile, candidate)
        weighted_candidates.append({**candidate, **weighted_candidate})
    
    print("\nCalculating final scores...")
    sorted_candidates = sorted(
        weighted_candidates,
        key=lambda x: sum([
            x.get('InformacionAcademica', {}).get('AreaEstudio', 0) +
            x.get('InformacionAcademica', {}).get('NivelEstudio', 0) +
            x.get('InformacionAcademica', {}).get('FormacionAdicional', 0) +
            x.get('ExperienciaLaboral', {}).get('AniosExperiencia', 0) +
            x.get('ExperienciaLaboral', {}).get('AniosLiderandoTransformacionInnovacion', 0) +
            x.get('ExperienciaLaboral', {}).get('ImplementacionProyectosEstrategicos', 0) +
            x.get('ConocimientosTecnicos', {}).get('MetodologiasAgiles', 0) +
            x.get('ConocimientosTecnicos', {}).get('GestionProyectosInnovacion', 0) +
            x.get('ConocimientosTecnicos', {}).get('HerramientasGestionCambio', 0) +
            x.get('ConocimientosTecnicos', {}).get('TecnologiasEmergentes', 0) +
            x.get('Habilidades', {}).get('HabilidadesBlandas', 0) +
            x.get('Habilidades', {}).get('HabilidadesTecnicas', 0)

        ]),
        reverse=True
    )
    
    top_5_candidates = sorted_candidates[:5]
    print(f"\nTop 5 candidates selected from {len(candidates)} total candidates")
    print("=== Candidate comparison completed ===\n")
    return top_5_candidates

def generate_recomendation(ideal_profile) -> List[Dict]:
    print("\n=== Starting recommendation generation ===")

    db = MongoConnection()
    candidates = db.get_extracted_fields_without_personal_info()
    candidates_dicts = [c for c in candidates]  # Conversión a diccionarios
    print(f"Retrieved {len(candidates_dicts)} candidates from database")

    top_5_candidates = compare_candidates(ideal_profile, candidates_dicts)  # Pasar diccionarios

    # Actualizar los candidatos en la base de datos
    for candidate in top_5_candidates:
        print(f"Updating candidate with id {candidate.get('_id', 'Unknown')}")
        db.update_candidate(candidate.get('_id'), candidate)  # Asegura que update_candidate recibe el ID y el objeto completo
        print(f"Candidate with id {candidate.get('_id', 'Unknown')} updated successfully")

    print("\nFinal Recommendations:")
    for i, candidate in enumerate(top_5_candidates, 1):
        print(f"\nRank {i}:")
        print(json.dumps(candidate, indent=2))

    print("=== Recommendation generation completed ===\n")
    return top_5_candidates