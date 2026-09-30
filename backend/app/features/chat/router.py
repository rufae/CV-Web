"""Router del chat.

Rutas canónicas: `POST /api/chat` (JSON hasta T4.5, luego SSE).
Alias temporal de compatibilidad: `POST /ask` (se retira en T5.7).
"""

from fastapi import APIRouter, Depends, Request

from app.core.ratelimit import enforce_daily_budget, enforce_rate_limit
from app.features.chat.schemas import Prompt
from app.features.chat.service import ChatService

router = APIRouter(tags=["chat"])


async def _chat_limits(request: Request) -> None:
    enforce_rate_limit(request, "chat_limiter")
    enforce_daily_budget(request)


@router.post("/api/chat", dependencies=[Depends(_chat_limits)])
@router.post("/ask", include_in_schema=False, dependencies=[Depends(_chat_limits)])
async def ask_rafa(prompt: Prompt, request: Request) -> dict[str, str]:
    service: ChatService = request.app.state.chat_service
    return {"response": await service.ask(prompt.message)}
