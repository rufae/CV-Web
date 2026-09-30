"""Router de contacto.

Rutas canónicas: `POST /api/contact`.
Alias temporal de compatibilidad: `POST /contact` (se retira en T5.7).
"""

from fastapi import APIRouter, Depends, Request

from app.core.ratelimit import enforce_budget, enforce_rate_limit
from app.features.contact.schemas import ContactForm
from app.features.contact.service import ContactService

router = APIRouter(tags=["contact"])


async def _contact_limits(request: Request) -> None:
    enforce_rate_limit(request, "contact_limiter")
    enforce_budget(request, "contact_budget")


@router.post("/api/contact", dependencies=[Depends(_contact_limits)])
@router.post("/contact", include_in_schema=False, dependencies=[Depends(_contact_limits)])
async def send_email(form: ContactForm, request: Request) -> dict[str, str]:
    service: ContactService = request.app.state.contact_service
    await service.send(form)
    return {"status": "Mensaje enviado correctamente"}
