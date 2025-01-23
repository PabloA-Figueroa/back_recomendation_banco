from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

from app.models.personal_map_mongos import ProfileModel


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
    output_parser = JsonOutputParser(pydantic_object=ProfileModel)
    example_profile = {
  "Secciones": [
    {
      "name": "Información Academica",
      "Subsecciones": [
        {
          "name": "Área de estudio",
          "values": [
            {
              "name": "Ingenieria Informatica",
              "ponderacion": 0
            }
          ],
          "ponderacion": 0
        },
        {
          "name": "Nivel de estudio",
          "values": [
            {
              "name": "Grado",
              "ponderacion": 0
            }
          ],
          "ponderacion": 0
        },
        {
          "name": "Estado de estudio",
          "values": [
            {
              "name": "Terminado",
              "ponderacion": 0
            }
          ],
          "ponderacion": 0
        }
      ],
      "ponderacion": 9
    },
    {
      "name": "Experience Laboral",
      "Subsecciones": [
        {
          "name": "Nombre del puesto",
          "values": [
            {
              "name": "Desarrollador Backend",
              "ponderacion": 0
            }
          ],
          "ponderacion": 0
        },
        {
          "name": "Jerarquía",
          "values": [
            {
              "name": "Junior/Mid",
              "ponderacion": 0
            }
          ],
          "ponderacion": 0
        }
      ],
      "ponderacion": 7
    },
    {
      "name": "Habilidades",
      "Subsecciones": [
        {
          "name": "Habilidades blandas",
          "values": [
            {
              "name": "habla",
              "ponderacion": 0
            },
            {
              "name": "liderazgo",
              "ponderacion": 0
            }
          ],
          "ponderacion": 0
        },
        {
          "name": "Habilidades técnicas",
          "values": [
            {
              "name": "python",
              "ponderacion": 0
            },
            {
              "name": "java",
              "ponderacion": 0
            }
          ],
          "ponderacion": 9
        }
      ],
      "ponderacion": 9
    }
  ],
  "Tag": "Desarrollo de Software"
}

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            Eres un experto en recursos humanos y debes generar un perfil ideal para un puesto de trabajo, siguiendo el formato json especificado.
            Debes incluir las ponderaciones que debería tener cada campo para dar mayor importancia a los campos relevantes.
            Los valores deben ser los más adecuados, teniendo en cuenta el puesto de trabajo.
            Ademas cada una de las habilidades ya sean blandas o tecnicas debe tener una ponderación de importancia.
            No debes añadir ningún comentario adicional al texto, solo la respuesta en formato JSON.
            {format_instructions}
            Ademas adjunto un ejemplo de un perfil ideal en formato json:
            {ideal_profile_json}
            En caso de que existan posibles valores ideales para el puesto  agregalo igualmente con su ponderacion, no te limites a una respues por valor.

            """),
            ("user", "Genera un perfil ideal en formato json, siguiendo el modelo pydantic, con la siguiente descripción del puesto: {job_description}"),
        ]
    )
    format_instructions = output_parser.get_format_instructions()
    chain = prompt | model | output_parser
    #result = chain.invoke({"job_description": job_description,  "format_instructions": format_instructions}).content.strip()
    result = chain.invoke({"job_description": job_description,  "format_instructions": format_instructions,"ideal_profile_json":example_profile })
    # Parse the JSON response
    return result

def generar(promp):
    job_description =promp
    #"Desarrollador de Software con experiencia en Python y Django, con conocimientos de bases de datos y desarrollo front-end. Se requiere alta capacidad para trabajar en equipo y buenas habilidades de comunicación."
    ideal_profile = generate_ideal_profile(job_description)
    return ideal_profile