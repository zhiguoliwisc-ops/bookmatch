from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_identification import IdentificationStatus
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.book_identification_service import BookIdentificationService
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.exceptions import (
    AmbiguousBookError,
    BookNotFoundError,
)


class CandidateBookResolver(BookResolver):
    """Resolve a book using candidate retrieval and identification."""

    def __init__(
        self,
        candidate_service: BookCandidateService,
        identification_service: BookIdentificationService,
    ) -> None:
        self.candidate_service = candidate_service
        self.identification_service = identification_service

    def resolve(
        self,
        book: BookInput,
    ) -> EnrichedBook:
        """Resolve a book input to an identified enriched book."""

        candidates = self.candidate_service.find_candidates(book)

        identification = self.identification_service.identify(
            book,
            candidates,
        )

        if identification.status in {
            IdentificationStatus.EXACT_MATCH,
            IdentificationStatus.CORRECTED_MATCH,
        }:
            if identification.matched_book is None:
                raise BookNotFoundError(
                    "Book identification returned a match status "
                    "without a matched book."
                )

            return identification.matched_book

        if identification.status == IdentificationStatus.AMBIGUOUS:
            raise AmbiguousBookError(
                identification.reason
            )

        raise BookNotFoundError(
            identification.reason
        )