from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv
import json
from app.models.personal_map import ProfileModel
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
model = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    temperature=1,
    api_key=os.getenv('GEMINI_API_KEY')
)
def generate_ideal_profile(job_description: str) -> dict:
    """
    Generates an ideal profile for a job description, using Langchain and OpenAI.
    """
    output_parser = PydanticOutputParser(pydantic_object=ProfileModel)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            Eres un experto en recursos humanos y debes generar un perfil ideal para un puesto de trabajo, siguiendo el formato json especificado.
            Debes incluir las ponderaciones que debería tener cada campo para dar mayor importancia a los campos relevantes.
            Los valores deben ser los más adecuados, teniendo en cuenta el puesto de trabajo.
            Ademas cada una de las habilidades ya sean blandas o tecnicas debe tener una ponderación de importancia.
            No debes añadir ningún comentario adicional al texto, solo la respuesta en formato JSON.
            {format_instructions}
            """),
            ("user", "Genera un perfil ideal en formato json, siguiendo el modelo pydantic, con la siguiente descripción del puesto: {job_description}"),
        ]
    )
    format_instructions = output_parser.get_format_instructions()
    chain = prompt | model
    result = chain.invoke({"job_description": job_description,  "format_instructions": format_instructions})
    return result.model_dump()

def ejecutar():
    job_description = "Desarrollador de Software con experiencia en Python y Django, con conocimientos de bases de datos y desarrollo front-end. Se requiere alta capacidad para trabajar en equipo y buenas habilidades de comunicación."
    ideal_profile = generate_ideal_profile(job_description)
    return ideal_profile