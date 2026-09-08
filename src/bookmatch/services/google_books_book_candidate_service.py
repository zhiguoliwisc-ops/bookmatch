from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import (
    BookCandidateService,
)
from bookmatch.services.google_books_client import (
    GoogleBooksClient,
)


class GoogleBooksBookCandidateService(BookCandidateService):
    """Retrieve book candidates from Google Books."""

    def __init__(
        self,
        api_key: str,
    ) -> None:
        self.client = GoogleBooksClient(
            api_key=api_key,
        )

    def find_candidates(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        """Return Google Books candidates for the input book."""

        data = self.client.get(
            {
                "q": self._build_query(book),
            }
        )

        return self._create_candidates(data)

    @staticmethod
    def _build_query(
        book: BookInput,
    ) -> str:
        query_parts = [
            f'intitle:"{book.title}"',
        ]

        if book.author:
            query_parts.append(
                f'inauthor:"{book.author}"'
            )

        return "+".join(query_parts)

    @staticmethod
    def _create_candidates(
        data: dict,
    ) -> list[BookCandidate]:
        candidates = []

        for item in data.get("items", []):
            volume_info = item.get(
                "volumeInfo",
                {},
            )

            title = volume_info.get("title")

            if not title:
                continue

            authors = volume_info.get(
                "authors",
                [],
            )

            author = ", ".join(authors) or None

            identifiers = volume_info.get(
                "industryIdentifiers",
                [],
            )

            isbn = None

            for identifier in identifiers:
                if identifier.get("type") in {
                    "ISBN_13",
                    "ISBN_10",
                }:
                    isbn = identifier.get("identifier")
                    break

            enriched_book = EnrichedBook(
                title=title,
                author=author,
                publication_date=volume_info.get(
                    "publishedDate"
                ),
                isbn=isbn,
                description=volume_info.get(
                    "description"
                ),
                source="Google Books",
            )

            candidates.append(
                BookCandidate(
                    book=enriched_book,
                    provider="Google Books",
                )
            )

        return candidates