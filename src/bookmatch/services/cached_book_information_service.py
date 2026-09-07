from bookmatch.models.book import BookInput, EnrichedBook

from bookmatch.services.book_information_service import (
    BookInformationService,
)


class CachedBookInformationService(BookInformationService):
    """Cache book information returned by another service."""

    def __init__(
        self,
        underlying_service: BookInformationService,
    ) -> None:
        self.underlying_service = underlying_service
        self._cache: dict[str, EnrichedBook] = {}

    def enrich(
        self,
        book: BookInput,
    ) -> EnrichedBook:
        key = self._create_cache_key(book)

        if key in self._cache:
            return self._cache[key]

        enriched_book = self.underlying_service.enrich(book)

        self._cache[key] = enriched_book

        return enriched_book

    @staticmethod
    def _create_cache_key(
        book: BookInput,
    ) -> str:
        if book.isbn:
            return f"isbn:{book.isbn}"

        author = book.author or ""

        return (
            f"title:{book.title.strip().lower()}"
            f"|author:{author.strip().lower()}"
        )
