from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.exceptions import BookInformationServiceError


class CompositeBookCandidateService(BookCandidateService):
    """Try candidate services in order until candidates are found."""

    def __init__(
        self,
        services: list[BookCandidateService],
    ) -> None:
        self.services = services

    def find_candidates(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        if not self.services:
            raise ValueError(
                "At least one candidate service must be configured."
            )

        for service in self.services:
            try:
                candidates = service.find_candidates(book)
            except BookInformationServiceError:
                continue

            if candidates:
                return candidates

        return []