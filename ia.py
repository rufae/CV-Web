from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API key de Gemini no encontrada en el archivo .env")

client = genai.Client(api_key=GEMINI_API_KEY)

with open("rafa_context.txt", "r", encoding="utf-8") as f:
    rafa_context = f.read()

ask_rafa_endpoint = APIRouter()

class Prompt(BaseModel):
    message: str

@ask_rafa_endpoint.post("/ask")
async def ask_rafa(prompt: Prompt):
    full_prompt = (
        f"Eres una IA que responde preguntas como si fueses Rafael Castaño, un desarrollador.\n"
        f"Tu misión es contestar siempre de forma clara y concisa, con respuestas breves y directas, "
        f"para que el usuario pueda leerlas fácilmente en pantalla. "
        f"No extiendas demasiado la respuesta salvo que el usuario pida explícitamente una explicación detallada.\n\n"
        f"Aquí tienes toda la información relevante sobre Rafael:\n{rafa_context}\n\n"
        f"Pregunta: {prompt.message}\n\n"
        f"Recuerda ser conciso, excepto si el usuario pide detalle."
        f"Si el usuario te pregunta algo que no esta relacionado con saber algo sobre Rafael Castaño debes decirle que no puede hacer preguntas que no sean para conocer a Rafael pero de una manera profesional y limpia"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    return {"response": response.text}
