from abc import ABC, abstractmethod

from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book import BookInput
from bookmatch.models.book_resolution import BookResolution

from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_identification import IdentificationStatus
from bookmatch.models.book_resolution import (
    BookResolution,
    ResolutionDecision,
)
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)

class BookResolutionService(ABC):
    """Interface for resolving book candidates."""

    @abstractmethod
    def resolve(
        self,
        book: BookInput,
        candidates: list[BookCandidate],
    ) -> BookResolution:
        """Resolve candidates into an automatic or user-assisted decision."""
        raise NotImplementedError

class BookResolutionServiceImpl(BookResolutionService):
    """Resolve book candidates into an automatic or user-assisted decision."""

    def __init__(
        self,
        identification_service: BookIdentificationService,
    ) -> None:
        self.identification_service = identification_service

    def resolve(
        self,
        book: BookInput,
        candidates: list[BookCandidate],
    ) -> BookResolution:
        identification = self.identification_service.identify(
            book,
            candidates,
        )

        if identification.status in {
            IdentificationStatus.EXACT_MATCH,
            IdentificationStatus.CORRECTED_MATCH,
        }:
            if identification.matched_book is None:
                raise ValueError(
                    "Identification returned a match without a matched book."
                )

            return BookResolution(
                decision=ResolutionDecision.AUTO_RESOLVE,
                selected_book=identification.matched_book,
            )

        if identification.status == IdentificationStatus.AMBIGUOUS:
            return BookResolution(
                decision=ResolutionDecision.ASK_USER,
                candidates=[
                    candidate.book
                    for candidate in candidates
                ],
            )

        return BookResolution(
            decision=ResolutionDecision.NOT_FOUND,
        )