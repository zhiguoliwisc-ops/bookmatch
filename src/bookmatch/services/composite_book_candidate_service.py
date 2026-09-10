from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.candidate_deduplication import (
    deduplicate_candidates,
)
from bookmatch.services.exceptions import BookInformationServiceError


class CompositeBookCandidateService(BookCandidateService):
    """Combine candidates from multiple candidate services."""

    def __init__(self, services: list[BookCandidateService]) -> None:
        self.services = services

    def find_candidates(self, book: BookInput) -> list[BookCandidate]:
        if not self.services:
            raise ValueError(
                "At least one candidate service must be configured."
            )

        candidates: list[BookCandidate] = []
        provider_failures = 0

        for service in self.services:
            try:
                service_candidates = service.find_candidates(book)
            except BookInformationServiceError:
                provider_failures += 1
                continue

            candidates.extend(service_candidates)

        if not candidates and provider_failures == len(self.services):
            raise BookInformationServiceError(
                "All book information providers failed."
            )

        return deduplicate_candidates(candidates)