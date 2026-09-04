import httpx

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)

from bookmatch.services.book_information_service import (
    BookInformationService,
)


class GoogleBooksBookInformationService(BookInformationService):
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

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

    def _get(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        try:
            response = httpx.get(
                url,
                timeout=10.0,
                **kwargs,
            )
            response.raise_for_status()

            return response

        except httpx.TimeoutException as error:
            raise BookInformationServiceError(
                "The request to Google Books timed out."
            ) from error

        except httpx.HTTPStatusError as error:
            raise BookInformationServiceError(
                f"Google Books returned HTTP "
                f"{error.response.status_code}."
            ) from error

        except httpx.RequestError as error:
            raise BookInformationServiceError(
                "Could not connect to Google Books."
            ) from error

    def _lookup_by_isbn(
        self,
        book: BookInput,
    ) -> EnrichedBook | None:
        params = {
            "q": f"isbn:{book.isbn}",
        }

        response = self._get(
            self.BASE_URL,
            params=params,
        )

        return self._create_enriched_book(
            response.json(),
            book,
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

        response = self._get(
            self.BASE_URL,
            params=params,
        )

        return self._create_enriched_book(
            response.json(),
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