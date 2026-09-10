from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_identification import (
    BookIdentification,
    IdentificationStatus,
)
import unicodedata
import re


class BookIdentificationService:
    """Identify the best matching book from metadata candidates."""

    def _author_matches_evidence(
        self,
        book: BookInput,
        candidate: BookCandidate,
    ) -> bool:
        """Return whether evidence supports the input author."""

        if not book.author:
            return True

        if candidate.evidence is None:
            return False

        if not candidate.evidence.author:
            return False

        return self._author_names_match(
            book.author,
            candidate.evidence.author,
        )

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

        # When the input contains only a title, prefer exact-title
        # candidates over longer subtitle/series candidates.
        if not book.author:
            exact_title_candidates = [
                candidate
                for candidate in matching_candidates
                if self._titles_are_exact(
                    book.title,
                    candidate.book.title,
                )
            ]

            if exact_title_candidates:
                matching_candidates = exact_title_candidates

        if not matching_candidates:
            evidence_match = self._identify_by_evidence(
                book,
                candidates,
            )

            if evidence_match is not None:
                return evidence_match

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
            if self._same_book_identity(matching_candidates):
                candidate = matching_candidates[0]

                return BookIdentification(
                    status=IdentificationStatus.EXACT_MATCH,
                    matched_book=candidate.book,
                    confidence=1.0,
                    reason=(
                        "Multiple editions match the same title "
                        "and author."
                    ),
                )

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

    def _identify_by_evidence(
        self,
        book: BookInput,
        candidates: list[BookCandidate],
    ) -> BookIdentification | None:
        """Identify a canonical book using candidate evidence."""

        input_series, input_volume = self._parse_series_volume(
            book.title,
        )

        if input_series is None or input_volume is None:
            return None

        evidence_matches = [
            candidate
            for candidate in candidates
            if candidate.evidence is not None
            and candidate.evidence.series_title is not None
            and candidate.evidence.volume_number is not None
            and candidate.evidence.canonical_title is not None
            and self._normalize(
                candidate.evidence.series_title
            )
            == self._normalize(input_series)
            and candidate.evidence.volume_number == input_volume
            and self._author_matches_evidence(
                book,
                candidate,
            )
        ]

        if not evidence_matches:
            return None

        canonical_titles = {
            self._normalize(
                candidate.evidence.canonical_title
            )
            for candidate in evidence_matches
            if candidate.evidence is not None
            and candidate.evidence.canonical_title is not None
        }

        if len(canonical_titles) != 1:
            return BookIdentification(
                status=IdentificationStatus.AMBIGUOUS,
                matched_book=None,
                confidence=0.5,
                reason=(
                    "Multiple canonical titles match the "
                    "series and volume evidence."
                ),
            )

        canonical_title = next(iter(canonical_titles))

        canonical_candidates = [
            candidate
            for candidate in candidates
            if self._normalize(candidate.book.title)
            == canonical_title
            and self._author_matches(
                book,
                candidate.book,
            )
        ]

        if len(canonical_candidates) != 1:
            return None

        candidate = canonical_candidates[0]

        return BookIdentification(
            status=IdentificationStatus.EXACT_MATCH,
            matched_book=candidate.book,
            confidence=1.0,
            reason=(
                "Series and volume evidence identifies "
                "the canonical book."
            ),
        )

    def _evidence_matches_input(
        self,
        book: BookInput,
        candidate: BookCandidate,
    ) -> bool:
        """Return whether candidate evidence matches the input."""

        evidence = candidate.evidence

        if evidence is None:
            return False

        if not evidence.series_title:
            return False

        if evidence.volume_number is None:
            return False

        if not evidence.canonical_title:
            return False

        if not evidence.author:
            return False

        if not self._author_names_match(
            book.author or "",
            evidence.author,
        ):
            return False

        input_series, input_volume = (
            self._parse_series_volume(book.title)
        )

        if input_series is None or input_volume is None:
            return False

        return (
            self._normalize(input_series)
            == self._normalize(evidence.series_title)
            and input_volume == evidence.volume_number
        )

    @staticmethod
    def _parse_series_volume(
        title: str,
    ) -> tuple[str | None, int | None]:
        """Extract a series title and volume number from an input title."""

        normalized_title = " ".join(title.split())

        marker = " Vol. "

        if marker not in normalized_title:
            return None, None

        series_title, volume_text = normalized_title.rsplit(
            marker,
            1,
        )

        try:
            volume_number = int(volume_text)
        except ValueError:
            return None, None

        if not series_title:
            return None, None

        return series_title, volume_number

    def _same_book_identity(
        self,
        candidates: list[BookCandidate],
    ) -> bool:
        """Return whether all candidates represent the same book work."""
        if not candidates:
            return False

        first = candidates[0]

        for candidate in candidates[1:]:
            if not self._titles_match_as_same_work(
                first.book.title,
                candidate.book.title,
            ):
                return False

            if not self._author_names_match(
                first.book.author,
                candidate.book.author,
            ):
                return False

        return True

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize text for comparison."""

        normalized = value.casefold()
        normalized = re.sub(r"[^\w\s:]", " ", normalized)

        return " ".join(normalized.split())
    
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
        if not book.author:
            return True

        if not candidate.author:
            return False

        return self._author_names_match(
            book.author,
            candidate.author,
        )

    @classmethod
    def _author_names_match(
        cls,
        first: str | None,
        second: str | None,
    ) -> bool:
        if not first or not second:
            return False

        first_normalized = cls._normalize_author(first)
        second_normalized = cls._normalize_author(second)

        if first_normalized == second_normalized:
            return True

        first_parts = first_normalized.split()
        second_parts = second_normalized.split()

        return (
            len(first_parts) > 1
            and len(first_parts) == len(second_parts)
            and sorted(first_parts) == sorted(second_parts)
        )

    @classmethod
    def _normalize_author(
        cls,
        value: str,
    ) -> str:
        """Normalize an author name for conservative matching."""

        normalized = unicodedata.normalize(
            "NFKC",
            value,
        )

        normalized = (
            normalized
            .replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
        )

        normalized = cls._normalize(normalized)

        replacements = {
            "madeline": "madeleine",
        }

        parts = [
            replacements.get(part, part)
            for part in normalized.split()
        ]

        return " ".join(parts)

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
            or input_title.startswith(
                candidate_title + ":"
            )
        )

    def _titles_match_as_same_work(
        self,
        first_title: str,
        second_title: str,
    ) -> bool:
        """Return whether two titles represent the same book work."""
        first_normalized = self._normalize(first_title)
        second_normalized = self._normalize(second_title)

        return (
            first_normalized == second_normalized
            or first_normalized.startswith(
                second_normalized + ":"
            )
            or second_normalized.startswith(
                first_normalized + ":"
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