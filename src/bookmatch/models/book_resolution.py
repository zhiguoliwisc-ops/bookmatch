from enum import Enum

from pydantic import BaseModel

from bookmatch.models.book import EnrichedBook


class ResolutionDecision(str, Enum):
    AUTO_RESOLVE = "auto_resolve"
    ASK_USER = "ask_user"
    NOT_FOUND = "not_found"


class BookResolution(BaseModel):
    decision: ResolutionDecision
    selected_book: EnrichedBook | None = None
    candidates: list[EnrichedBook] = []