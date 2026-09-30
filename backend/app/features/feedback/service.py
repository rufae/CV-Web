"""Servicio de feedback (T4.9)."""

from app.features.feedback.schemas import FeedbackRequest
from app.features.feedback.store import FeedbackStore


class FeedbackService:
    def __init__(self, store: FeedbackStore) -> None:
        self.store = store

    def record(self, payload: FeedbackRequest) -> bool:
        return self.store.add(payload)
