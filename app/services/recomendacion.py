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
from data.database.mysql import MySqlConnection

load_dotenv()

# Configuración del modelo
model = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    temperature=1,
    api_key=os.getenv('GEMINI_API_KEY')
)

def assign_weights_to_candidate(ideal_profile: Dict, candidate: Dict) -> Dict:
    """
    Asigna pesos a las características de un candidato en función del perfil ideal.
    """
    # Configuración del JsonOutputParser
    parser = JsonOutputParser(pydantic_object=ProfileModel)
    
    # Definición del prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            Eres un experto en recursos humanos y debes asignar pesos a las características de un candidato en función de un perfil ideal.
            Debes comparar las características del candidato con el perfil ideal y asignar un peso a cada característica del candidato.
            {format_instructions}
            """),
            ("user", """
            Perfil ideal: {ideal_profile}
            Candidato: {candidate}
            Asigna pesos a las características del candidato en función del perfil ideal.
            """),
        ]
    )
    
    # Obtener las instrucciones de formato del parser
    format_instructions = parser.get_format_instructions()
    
    # Crear la cadena de procesamiento
    chain = prompt | model | parser
    
    # Invocar la cadena con los datos de entrada
    result = chain.invoke({
        "ideal_profile": json.dumps(ideal_profile),
        "candidate": json.dumps(candidate.dict()),
        "format_instructions": format_instructions
    })
    
    print("RESULTADO (después de parsear): ", result)  # Verificar el JSON parseado
    return result

def compare_candidates(ideal_profile: Dict, candidates: List[Dict]) -> List[Dict]:
    """
    Compara las ponderaciones de los candidatos y selecciona los 5 mejores.
    """
    print("Comparación de candidatos...")
    weighted_candidates = []
    for candidate in candidates:
        print("Procesando candidato...")
        weighted_candidate = assign_weights_to_candidate(ideal_profile, candidate)
        print("Candidato con pesos asignados: ", weighted_candidate)
        weighted_candidates.append(weighted_candidate)
    
    print("Candidatos con pesos asignados: ", weighted_candidates)
    
    # Ordenar los candidatos por la suma de sus ponderaciones
    sorted_candidates = sorted(
        weighted_candidates,
        key=lambda x: sum([
            x.get('informacion_academica_ponderacion', 0),
            x.get('idioma_ponderacion', 0),
            x.get('experiencia_laboral_ponderacion', 0),
            x.get('habilidades_ponderacion', 0)
        ]),
        reverse=True
    )
    
    print("Candidatos ordenados: ", sorted_candidates)
    
    # Seleccionar los 5 mejores candidatos
    top_5_candidates = sorted_candidates[:5]
    print("Top 5 candidatos: ", top_5_candidates)
    return top_5_candidates

def generate_recomendation():
    """
    Función principal para generar recomendaciones de candidatos.
    """
    # Generar el perfil ideal
    job_description = "Desarrollador de Software con experiencia en Python y Django, con conocimientos de bases de datos y desarrollo front-end. Se requiere alta capacidad para trabajar en equipo y buenas habilidades de comunicación."
    ideal_profile = generate_ideal_profile(job_description)
    
    # Obtener los candidatos desde la base de datos
    db = MySqlConnection()
    candidates = db.get_all_candidates()
    print("Candidatos obtenidos de la base de datos: ", candidates)
    
    # Comparar y seleccionar los 5 mejores candidatos
    top_5_candidates = compare_candidates(ideal_profile, candidates)
    
    # Imprimir los 5 mejores candidatos
    print("Recomendación final:")
    for candidate in top_5_candidates:
        print(candidate)
    return top_5_candidates