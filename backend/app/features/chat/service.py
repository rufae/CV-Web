"""Servicio del chat: respuestas con Google Gemini sobre el contexto de Rafael."""

from fastapi import HTTPException
from google import genai
from google.genai import types

from app.core.config import Settings

PROMPT_TEMPLATE = (
    "Eres una IA que responde preguntas como si fueses Rafael Castaño, un desarrollador.\n"
    "Tu misión es contestar siempre de forma clara y concisa, con respuestas breves y directas, "
    "para que el usuario pueda leerlas fácilmente en pantalla. "
    "No extiendas demasiado la respuesta salvo que el usuario pida explícitamente una explicación "
    "detallada.\n\n"
    "Aquí tienes toda la información relevante sobre Rafael:\n{context}\n\n"
    "Pregunta: {message}\n\n"
    "Recuerda ser conciso, excepto si el usuario pide detalle."
    "Si el usuario te pregunta algo que no esta relacionado con saber algo sobre Rafael Castaño "
    "debes decirle que no puede hacer preguntas que no sean para conocer a Rafael pero de una "
    "manera profesional y limpia"
)


def build_prompt(context: str, message: str) -> str:
    return PROMPT_TEMPLATE.format(context=context, message=message)


class ChatService:
    def __init__(self, settings: Settings, context: str | None) -> None:
        self._settings = settings
        self._context = context
        self._client: genai.Client | None = None

    @property
    def enabled(self) -> bool:
        return self._settings.chat_enabled and self._context is not None

    def _client_or_raise(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._settings.google_api_key)
        return self._client

    async def ask(self, message: str) -> str:
        if not self.enabled:
            raise HTTPException(
                status_code=503,
                detail="El asistente no está disponible ahora mismo.",
            )
        response = self._client_or_raise().models.generate_content(
            model=self._settings.gemini_model,
            contents=build_prompt(self._context or "", message),
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        return response.text or ""
