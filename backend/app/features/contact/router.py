"""Router de contacto.

Rutas canónicas: `POST /api/contact`.
Alias temporal de compatibilidad: `POST /contact` (se retira en T5.7).
"""

from fastapi import APIRouter, Request

from app.features.contact.schemas import ContactForm
from app.features.contact.service import ContactService

router = APIRouter(tags=["contact"])


@router.post("/api/contact")
@router.post("/contact", include_in_schema=False)
async def send_email(form: ContactForm, request: Request) -> dict[str, str]:
    service: ContactService = request.app.state.contact_service
    await service.send(form)
    return {"status": "Mensaje enviado correctamente"}
