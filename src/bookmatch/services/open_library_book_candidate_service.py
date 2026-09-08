import httpx

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import (
    BookCandidateService,
)
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)


class OpenLibraryBookCandidateService(BookCandidateService):
    """Retrieve book candidates from Open Library."""

    BASE_URL = "https://openlibrary.org"

    HEADERS = {
        "User-Agent": "BookMatch/0.1",
    }

    def find_candidates(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        """Return Open Library candidates for the input book."""

        if book.isbn:
            candidates = self._lookup_by_isbn(book)

            if candidates:
                return candidates

        return self._lookup_by_title_and_author(book)

    def _get(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        try:
            response = httpx.get(
                url,
                headers=self.HEADERS,
                timeout=10.0,
                follow_redirects=True,
                **kwargs,
            )

            response.raise_for_status()
            return response

        except httpx.TimeoutException as error:
            raise BookInformationServiceError(
                "The request to Open Library timed out."
            ) from error

        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                return error.response

            raise BookInformationServiceError(
                f"Open Library returned HTTP "
                f"{error.response.status_code}."
            ) from error

        except httpx.RequestError as error:
            raise BookInformationServiceError(
                "Could not connect to Open Library."
            ) from error

    def _lookup_by_isbn(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        """Look up candidates by ISBN."""

        url = f"{self.BASE_URL}/isbn/{book.isbn}.json"

        response = self._get(url)

        if response.status_code == 404:
            return []

        try:
            data = response.json()
        except ValueError as error:
            raise BookInformationServiceError(
                "Open Library returned an invalid response."
            ) from error

        title = data.get("title")

        if not title:
            return []

        enriched_book = EnrichedBook(
            title=title,
            author=book.author,
            publication_date=book.publication_date,
            isbn=book.isbn,
            description=self._extract_description(data),
            source="Open Library",
        )

        return [
            BookCandidate(
                book=enriched_book,
                provider="Open Library",
            )
        ]

    def _lookup_by_title_and_author(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        """Look up candidates by title and optional author."""

        params = {
            "title": book.title,
        }

        if book.author:
            params["author"] = book.author

        response = self._get(
            f"{self.BASE_URL}/search.json",
            params=params,
        )

        try:
            data = response.json()
        except ValueError as error:
            raise BookInformationServiceError(
                "Open Library returned an invalid response."
            ) from error

        candidates = []

        for result in data.get("docs", []):
            title = result.get("title")

            if not title:
                continue

            enriched_book = EnrichedBook(
                title=title,
                author=self._extract_author(
                    result,
                    book,
                ),
                publication_date=self._extract_publication_date(
                    result,
                    book,
                ),
                isbn=self._extract_isbn(
                    result,
                    book,
                ),
                description=None,
                source="Open Library",
            )

            candidates.append(
                BookCandidate(
                    book=enriched_book,
                    provider="Open Library",
                )
            )

        return candidates

    @staticmethod
    def _extract_description(
        data: dict,
    ) -> str | None:
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