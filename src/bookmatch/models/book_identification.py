from enum import Enum

from pydantic import BaseModel, Field

from bookmatch.models.book import EnrichedBook


class IdentificationStatus(str, Enum):
    EXACT_MATCH = "exact_match"
    CORRECTED_MATCH = "corrected_match"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"


class BookIdentification(BaseModel):
    status: IdentificationStatus
    matched_book: EnrichedBook | None
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )
    reason: str