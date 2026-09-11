from enum import Enum

from pydantic import BaseModel, Field


class ReviewDecision(str, Enum):
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"


class ClassificationReview(BaseModel):
    """Structured review of a book classification."""

    decision: ReviewDecision
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )
    reason: str