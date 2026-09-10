from pydantic import BaseModel


class CandidateEvidence(BaseModel):
    """Structured evidence that helps identify a book candidate."""

    series_title: str | None = None
    volume_number: int | None = None
    author: str | None = None
    canonical_title: str | None = None