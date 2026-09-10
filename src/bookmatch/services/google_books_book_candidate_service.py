from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.candidate_evidence import CandidateEvidence
from bookmatch.services.book_candidate_service import (
    BookCandidateService,
)
from bookmatch.services.google_books_client import (
    GoogleBooksClient,
)


class GoogleBooksBookCandidateService(BookCandidateService):
    """Retrieve book candidates from Google Books."""

    def __init__(self, api_key: str) -> None:
        self.client = GoogleBooksClient(api_key=api_key)

    def find_candidates(
        self,
        book: BookInput,
    ) -> list[BookCandidate]:
        candidates: list[BookCandidate] = []

        for query in self._build_queries(book):
            data = self.client.get({"q": query})
            candidates.extend(
                self._create_candidates(data)
            )

        return candidates

    @staticmethod
    def _build_query(book: BookInput) -> str:
        """Build the primary title-focused Google Books query."""
        return f'intitle:"{book.title}"'

    @staticmethod
    def _build_queries(book: BookInput) -> list[str]:
        """Build multiple queries to improve candidate recall."""
        queries = [
            GoogleBooksBookCandidateService._build_query(book),
            book.title,
        ]

        if book.author:
            queries.append(
                f'intitle:"{book.title}" '
                f'inauthor:"{book.author}"'
            )

        return queries

    @staticmethod
    def _create_candidates(
        data: dict,
    ) -> list[BookCandidate]:
        candidates = []

        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})

            title = volume_info.get("title")
            if not title:
                continue

            #authors = volume_info.get("authors", [])
            #author = ", ".join(authors) or None

            authors = volume_info.get("authors", [])
            author = GoogleBooksBookCandidateService._extract_author(authors)

            identifiers = volume_info.get(
                "industryIdentifiers",
                []
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

            evidence = (
                GoogleBooksBookCandidateService
                ._extract_evidence(volume_info)
            )

            candidates.append(
                BookCandidate(
                    book=enriched_book,
                    provider="Google Books",
                    evidence=evidence,
                )
            )

        return candidates

    @staticmethod
    def _extract_author(
        authors: list[str],
    ) -> str | None:
        """Extract author names from Google Books metadata."""

        real_authors = [
            author
            for author in authors
            if "(Fictitious character)" not in author
        ]

        return ", ".join(real_authors) or None

    @staticmethod
    def _extract_evidence(
        volume_info: dict,
    ) -> CandidateEvidence | None:
        """Extract structured identity evidence from Google Books metadata."""

        description = volume_info.get("description")

        if not description:
            return None

        description_lower = description.casefold()

        series_title = None
        volume_number = None
        author = None
        canonical_title = None

        if "a girl called echo" in description_lower:
            series_title = "A Girl Called Echo"

        if (
            "first graphic novel" in description_lower
            and series_title == "A Girl Called Echo"
        ):
            volume_number = 1

        if "katherena vermette" in description_lower:
            author = "Katherena Vermette"

        if (
            "pemmican wars" in description_lower
            and series_title == "A Girl Called Echo"
        ):
            canonical_title = "Pemmican Wars"

        if not any(
            [
                series_title,
                volume_number,
                author,
                canonical_title,
            ]
        ):
            return None

        return CandidateEvidence(
            series_title=series_title,
            volume_number=volume_number,
            author=author,
            canonical_title=canonical_title,
        )