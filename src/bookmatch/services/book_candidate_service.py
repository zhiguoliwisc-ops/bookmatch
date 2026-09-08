from abc import ABC, abstractmethod

from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate


class BookCandidateService(ABC):
    """Interface for retrieving book candidates."""

    @abstractmethod
    def find_candidates(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        """Return candidate books matching the input."""
        raise NotImplementedError