from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.exceptions import (
    AmbiguousBookError,
    BookNotFoundError,
)

from bookmatch.models.book_resolution import ResolutionDecision
from bookmatch.services.book_resolution_service import (
    BookResolutionService,
)


class CandidateBookResolver(BookResolver):
    """Resolve a book using candidate retrieval and identification."""

    def __init__(
        self,
        candidate_service: BookCandidateService,
        resolution_service: BookResolutionService,
    ) -> None:
        self.candidate_service = candidate_service
        self.resolution_service = resolution_service

    def resolve(self, book: BookInput) -> EnrichedBook:
        candidates = self.candidate_service.find_candidates(book)

        resolution = self.resolution_service.resolve(
            book,
            candidates,
        )

        if resolution.decision == ResolutionDecision.AUTO_RESOLVE:
            if resolution.selected_book is None:
                raise BookNotFoundError(
                    "Resolution returned AUTO_RESOLVE without a selected book."
                )

            return resolution.selected_book

        if resolution.decision == ResolutionDecision.ASK_USER:
            raise AmbiguousBookError(
                "Multiple possible books were found.",
                candidates=resolution.candidates,
            )

        raise BookNotFoundError(
            "No matching book was found."
        )