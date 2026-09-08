from pydantic import BaseModel

from bookmatch.models.book import EnrichedBook


class BookCandidate(BaseModel):
    """A candidate book returned by a metadata provider."""

    book: EnrichedBook
    provider: str