"""Router del chat.

Rutas canónicas: `POST /api/chat`.
Alias temporal de compatibilidad: `POST /ask` (se retira en T5.7).
"""

from fastapi import APIRouter, Request

from app.features.chat.schemas import Prompt
from app.features.chat.service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/api/chat")
@router.post("/ask", include_in_schema=False)
async def ask_rafa(prompt: Prompt, request: Request) -> dict[str, str]:
    service: ChatService = request.app.state.chat_service
    return {"response": await service.ask(prompt.message)}
