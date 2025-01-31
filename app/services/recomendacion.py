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
            Debes comparar las características del candidato con el perfil ideal y asignar un peso a cada característica y subcaracterística del candidato.
            {format_instructions}
            Debes devolver con el mismo formato de entrada (JSON), pero con los pesos asignados y nuevos campos adicionales.            
            Conserva los datos existentes que ya tengan ponderaciones asignadas.
            """),
            ("user", """
            Perfil ideal: {ideal_profile}
            Candidato: {candidate}
            
            Instrucciones:
            1. Asignar pesos a características y subcaracterísticas basado en el perfil ideal
            2. Mantener ponderaciones existentes si ya existen
            3. Agregar tag del perfil ideal (si ya tiene tags, agregar uno nuevo)
            4. Incluir explicación detallada en el campo "explicacion"
            5. Crear campo "resumen_comparativo" con formato:
            "nombre_seccion": "X/10" (X = suma de ponderaciones en la sección)
            
            Ejemplo de resumen:
            "resumen_comparativo": {
                "Habilidades Técnicas": "5/10",
                "Experiencia Laboral": "7/10"
            }
            """)
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
        if isinstance(weighted_candidate,dict):
            weighted_candidates.append({**candidate, **weighted_candidate})
        else:
            weighted_candidates.append(candidate)
    
    print("\nCalculating final scores...")
    sorted_candidates = sorted(
        weighted_candidates,
        key=lambda x: sum([
             sum([sum(v.get("ponderacion",0) for v in sub.get("values",[]) if sub.get("values") ) for sub in sec.get("Subsecciones",[]) if sec.get("Subsecciones")  ] ) for sec in x.get('Secciones',[]) if x.get("Secciones")
        ]),
        reverse=True
    )
    
    top_5_candidates = sorted_candidates[:5]
    print(f"\nTop 5 candidates selected from {len(candidates)} total candidates")
    print("=== Candidate comparison completed ===\n")
    return top_5_candidates


def filter_unnecessary_sections(candidates: List[Dict]) -> List[Dict]:
    for candidate in candidates:
        secciones = candidate.get("Secciones", [])
        filtered_secciones = []
        for seccion in secciones:
            if seccion.get("ponderacion", 0) > 0 and seccion.get("name"):
                subsecciones = seccion.get("Subsecciones", [])
                filtered_subsecciones = []
                for subseccion in subsecciones:
                    if subseccion.get("ponderacion", 0) > 0 and subseccion.get("name"):
                        valores = [
                            valor for valor in subseccion.get("values", [])
                            if valor.get("ponderacion", 0) > 0 and valor.get("name")
                        ]
                        if valores:
                            subseccion["values"] = valores
                            filtered_subsecciones.append(subseccion)
                if filtered_subsecciones:
                    seccion["Subsecciones"] = filtered_subsecciones
                    filtered_secciones.append(seccion)
        candidate["Secciones"] = filtered_secciones
    return candidates

def generate_recomendation(ideal_profile) -> List[Dict]:
    print("\n=== Starting recommendation generation ===")

    db = MongoConnection()
    candidates = db.get_extracted_fields_without_personal_info()
    candidates_dicts = [c for c in candidates]
    print(f"Retrieved {len(candidates_dicts)} candidates from database")

    # Filtrar información innecesaria
    filtered_candidates = filter_unnecessary_sections(candidates_dicts)
    print(f"Filtered candidates to {len(filtered_candidates)} after removing unnecessary information")

    top_5_candidates = compare_candidates(ideal_profile, filtered_candidates)

    # Actualizar los candidatos en la base de datos
    for candidate in top_5_candidates:
        print(f"Updating candidate with id {candidate.get('_id', 'Unknown')}")
        db.update_candidate(candidate.get('_id'), candidate)
        print(f"Candidate with id {candidate.get('_id', 'Unknown')} updated successfully")

    print("\nFinal Recommendations:")
    for i, candidate in enumerate(top_5_candidates, 1):
        print(f"\nRank {i}:")
        print(json.dumps(candidate, indent=2))

    print("=== Recommendation generation completed ===\n")
    return top_5_candidates