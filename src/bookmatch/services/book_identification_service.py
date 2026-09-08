from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_identification import (
    BookIdentification,
    IdentificationStatus,
)


class BookIdentificationService:
    """Identify the best matching book from metadata candidates."""

    def identify(
        self,
        book: BookInput,
        candidates: list[BookCandidate],
    ) -> BookIdentification:
        """Identify a book using ISBN or title and author."""

        if not candidates:
            return BookIdentification(
                status=IdentificationStatus.NOT_FOUND,
                matched_book=None,
                confidence=0.0,
                reason="No candidate books were found.",
            )

        if book.isbn:
            return self._identify_by_isbn(
                book,
                candidates,
            )

        return self._identify_by_title_and_author(
            book,
            candidates,
        )

    def _identify_by_isbn(
        self,
        book: BookInput,
        candidates: list[BookCandidate],
    ) -> BookIdentification:
        """Identify a book using ISBN."""

        normalized_isbn = self._normalize_isbn(
            book.isbn
        )

        matching_candidates = [
            candidate
            for candidate in candidates
            if candidate.book.isbn
            and self._normalize_isbn(candidate.book.isbn)
            == normalized_isbn
        ]

        if len(matching_candidates) == 1:
            return BookIdentification(
                status=IdentificationStatus.EXACT_MATCH,
                matched_book=matching_candidates[0].book,
                confidence=1.0,
                reason="ISBN matches the candidate.",
            )

        if len(matching_candidates) > 1:
            return BookIdentification(
                status=IdentificationStatus.AMBIGUOUS,
                matched_book=None,
                confidence=0.5,
                reason=(
                    "Multiple candidates have the same ISBN."
                ),
            )

        return BookIdentification(
            status=IdentificationStatus.NOT_FOUND,
            matched_book=None,
            confidence=0.0,
            reason="No candidate matches the input ISBN.",
        )

    def _identify_by_title_and_author(
        self,
        book: BookInput,
        candidates: list[BookCandidate],
    ) -> BookIdentification:
        """Identify a book using title and author."""

        matching_candidates = [
            candidate
            for candidate in candidates
            if self._author_matches(book, candidate.book)
            and self._title_matches(book, candidate.book)
        ]

        if not matching_candidates:
            return BookIdentification(
                status=IdentificationStatus.NOT_FOUND,
                matched_book=None,
                confidence=0.0,
                reason=(
                    "No sufficiently matching candidate "
                    "was found."
                ),
            )

        if len(matching_candidates) > 1:
            return BookIdentification(
                status=IdentificationStatus.AMBIGUOUS,
                matched_book=None,
                confidence=0.5,
                reason=(
                    "Multiple candidates match the title "
                    "and author."
                ),
            )

        candidate = matching_candidates[0]

        if self._titles_are_exact(
            book.title,
            candidate.book.title,
        ):
            return BookIdentification(
                status=IdentificationStatus.EXACT_MATCH,
                matched_book=candidate.book,
                confidence=1.0,
                reason="Title and author match the input.",
            )

        return BookIdentification(
            status=IdentificationStatus.CORRECTED_MATCH,
            matched_book=candidate.book,
            confidence=0.95,
            reason=(
                "Input title matched a longer canonical "
                "title with the same author."
            ),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize text for comparison."""

        return " ".join(value.split()).casefold()

    @staticmethod
    def _normalize_isbn(isbn: str) -> str:
        """Normalize an ISBN by removing formatting characters."""

        return "".join(
            character
            for character in isbn
            if character.isalnum()
        ).upper()

    def _author_matches(
        self,
        book: BookInput,
        candidate: EnrichedBook,
    ) -> bool:
        """Return whether the candidate author matches."""

        if not book.author:
            return True

        if not candidate.author:
            return False

        return (
            self._normalize(book.author)
            == self._normalize(candidate.author)
        )

    def _title_matches(
        self,
        book: BookInput,
        candidate: EnrichedBook,
    ) -> bool:
        """Return whether the candidate title matches."""

        input_title = self._normalize(book.title)
        candidate_title = self._normalize(
            candidate.title
        )

        return (
            input_title == candidate_title
            or candidate_title.startswith(
                input_title + ":"
            )
        )

    def _titles_are_exact(
        self,
        input_title: str,
        candidate_title: str,
    ) -> bool:
        """Return whether two titles are exactly equal."""

        return (
            self._normalize(input_title)
            == self._normalize(candidate_title)
        )