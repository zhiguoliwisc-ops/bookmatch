import httpx

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.services.book_information_service import BookInformationService
from bookmatch.services.exceptions import (
    BookInformationServiceError,
    BookNotFoundError,
)

class OpenLibraryBookInformationService(BookInformationService):
    """Enrich book information using the Open Library API."""

    BASE_URL = "https://openlibrary.org"

    def _get(self, url: str, **kwargs) -> httpx.Response:
        try:
            return httpx.get(
                url,
                timeout=10.0,
                follow_redirects=True,
                **kwargs,
            )
        except httpx.TimeoutException as error:
            raise BookInformationServiceError(
                "The request to Open Library timed out."
            ) from error

        except httpx.RequestError as error:
            raise BookInformationServiceError(
                "Could not connect to Open Library."
            ) from error

    def enrich(self, book: BookInput) -> EnrichedBook:
        if book.isbn:
            enriched_book = self._lookup_by_isbn(book)

            if enriched_book:
                return enriched_book

        enriched_book = self._lookup_by_title_and_author(book)

        if enriched_book:
            return enriched_book

        raise BookNotFoundError(
            f"Could not find book: {book.title}"
        )

    def _lookup_by_isbn(
        self,
        book: BookInput,
    ) -> EnrichedBook | None:
        url = f"{self.BASE_URL}/isbn/{book.isbn}.json"

        response = self._get(
            url,            
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        #print("Status:", response.status_code)
        #print("Content-Type:", response.headers.get("content-type"))
        #print("Response preview:", response.text[:500])

        data = response.json()

        return EnrichedBook(
            title=data.get("title", book.title),
            author=book.author,
            publication_date=book.publication_date,
            isbn=book.isbn,
            description=self._extract_description(data),
            source="Open Library",
        )

    def _lookup_by_title_and_author(
        self,
        book: BookInput,
    ) -> EnrichedBook | None:
        params = {
            "title": book.title,
        }

        if book.author:
            params["author"] = book.author

        url = f"{self.BASE_URL}/search.json"

        response = self._get(
            url,
            params=params,
            )

        response.raise_for_status()

        data = response.json()

        docs = data.get("docs", [])

        if not docs:
            return None

        result = docs[0]

        return EnrichedBook(
            title=result.get("title", book.title),
            author=self._extract_author(result, book),
            publication_date=self._extract_publication_date(result, book),
            isbn=self._extract_isbn(result, book),
            description=None,
            source="Open Library",
        )

    @staticmethod
    def _extract_description(data: dict) -> str | None:
        description = data.get("description")

        if isinstance(description, dict):
            return description.get("value")

        if isinstance(description, str):
            return description

        return None

    @staticmethod
    def _extract_author(
        data: dict,
        book: BookInput,
    ) -> str | None:
        authors = data.get("author_name")

        if authors:
            return authors[0]

        return book.author

    @staticmethod
    def _extract_publication_date(
        data: dict,
        book: BookInput,
    ) -> str | None:
        year = data.get("first_publish_year")

        if year:
            return str(year)

        return book.publication_date

    @staticmethod
    def _extract_isbn(
        data: dict,
        book: BookInput,
    ) -> str | None:
        isbns = data.get("isbn")

        if isbns:
            return isbns[0]

        return book.isbn