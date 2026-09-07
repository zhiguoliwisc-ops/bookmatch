from pydantic import BaseModel

from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import BookClassification


class BookMatchResult(BaseModel):
    """Complete result of the BookMatch workflow."""

    book: EnrichedBook
    classification: BookClassification