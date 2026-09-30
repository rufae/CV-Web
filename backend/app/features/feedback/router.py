"""Router de feedback (T4.9)."""

from fastapi import APIRouter, Depends, Request

from app.core.ratelimit import enforce_rate_limit
from app.features.feedback.schemas import FeedbackRequest
from app.features.feedback.service import FeedbackService

router = APIRouter(tags=["feedback"])


async def _feedback_limits(request: Request) -> None:
    enforce_rate_limit(request, "feedback_limiter")


@router.post("/api/feedback", dependencies=[Depends(_feedback_limits)])
async def submit_feedback(payload: FeedbackRequest, request: Request) -> dict[str, str]:
    service: FeedbackService = request.app.state.feedback_service
    service.record(payload)
    return {"status": "ok"}
