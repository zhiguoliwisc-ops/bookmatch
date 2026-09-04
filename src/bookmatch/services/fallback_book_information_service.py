from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.services.book_information_service import (
    BookInformationService,
)
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)


class FallbackBookInformationService(BookInformationService):
    def __init__(
        self,
        primary: BookInformationService,
        fallback: BookInformationService,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def enrich(
        self,
        book: BookInput,
    ) -> EnrichedBook:
        try:
            return self.primary.enrich(book)
        except BookInformationServiceError:
            return self.fallback.enrich(book)