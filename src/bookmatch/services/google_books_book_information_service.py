from bookmatch.models.book import BookInput, EnrichedBook

from bookmatch.services.book_information_service import (
    BookInformationService,
)
from bookmatch.services.google_books_client import (
    GoogleBooksClient,
)

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)

class GoogleBooksBookInformationService(BookInformationService):
    """Retrieve book information from Google Books."""

    def __init__(
        self,
        api_key: str,
    ) -> None:
        self.client = GoogleBooksClient(
            api_key=api_key,
        )

    def enrich(
        self,
        book: BookInput,
    ) -> EnrichedBook:
        if book.isbn:
            enriched_book = self._lookup_by_isbn(book)

            if enriched_book:
                return enriched_book

        enriched_book = self._lookup_by_title_and_author(book)

        if enriched_book:
            return enriched_book

        raise BookInformationServiceError(
            f"Could not find book: {book.title}"
        )

    def _lookup_by_isbn(
        self,
        book: BookInput,
    ) -> EnrichedBook | None:
        params = {
            "q": f"isbn:{book.isbn}",
        }

        data = self.client.get(params)

        return self._create_enriched_book(
            data,
            book,
        )

    def _lookup_by_title_and_author(
        self,
        book: BookInput,
    ) -> EnrichedBook | None:
        query_parts = [
            f'intitle:"{book.title}"',
        ]

        if book.author:
            query_parts.append(
                f'inauthor:"{book.author}"'
            )

        params = {
            "q": "+".join(query_parts),
        }

        data = self.client.get(params)

        return self._create_enriched_book(
            data,
            book,
        )

    def _create_enriched_book(
        self,
        data: dict,
        book: BookInput,
    ) -> EnrichedBook | None:
        items = data.get("items", [])

        if not items:
            return None

        volume_info = items[0].get(
            "volumeInfo",
            {},
        )

        return EnrichedBook(
            title=volume_info.get(
                "title",
                book.title,
            ),
            author=", ".join(
                volume_info.get(
                    "authors",
                    [],
                )
            )
            or book.author,
            publication_date=volume_info.get(
                "publishedDate"
            ),
            isbn=self._extract_isbn(
                volume_info,
                book,
            ),
            description=volume_info.get(
                "description"
            ),
            source="Google Books",
        )

    def _extract_isbn(
        self,
        volume_info: dict,
        book: BookInput,
    ) -> str | None:
        identifiers = volume_info.get(
            "industryIdentifiers",
            [],
        )

        for identifier in identifiers:
            if identifier.get("type") in {
                "ISBN_13",
                "ISBN_10",
            }:
                return identifier.get("identifier")

        return book.isbn