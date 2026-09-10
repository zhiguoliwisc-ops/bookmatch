from pydantic import BaseModel

from bookmatch.models.book import EnrichedBook
from bookmatch.models.candidate_evidence import CandidateEvidence


class BookCandidate(BaseModel):
    """A candidate book returned by a metadata provider."""

    book: EnrichedBook
    provider: str
    evidence: CandidateEvidence | None = None