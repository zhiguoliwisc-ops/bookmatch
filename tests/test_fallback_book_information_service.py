from unittest.mock import Mock

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.services.fallback_book_information_service import (
    FallbackBookInformationService,
)

import pytest

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)

def test_enrich_returns_primary_result_when_primary_succeeds() -> None:
    primary = Mock()
    fallback = Mock()

    expected_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="A story about Wilbur.",
        source="Open Library",
    )

    primary.enrich.return_value = expected_book

    service = FallbackBookInformationService(
        primary=primary,
        fallback=fallback,
    )

    book = BookInput(
        title="Charlotte's Web",
    )

    result = service.enrich(book)

    assert result == expected_book
    primary.enrich.assert_called_once_with(book)
    fallback.enrich.assert_not_called()

def test_enrich_uses_fallback_when_primary_fails() -> None:
    primary = Mock()
    fallback = Mock()

    primary.enrich.side_effect = BookInformationServiceError(
        "Could not connect to Open Library."
    )

    expected_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="A story about Wilbur.",
        source="Google Books",
    )

    fallback.enrich.return_value = expected_book

    service = FallbackBookInformationService(
        primary=primary,
        fallback=fallback,
    )

    book = BookInput(
        title="Charlotte's Web",
    )

    result = service.enrich(book)

    assert result == expected_book

    primary.enrich.assert_called_once_with(book)
    fallback.enrich.assert_called_once_with(book)

def test_enrich_raises_error_when_primary_and_fallback_fail() -> None:
    primary = Mock()
    fallback = Mock()

    primary.enrich.side_effect = BookInformationServiceError(
        "Could not connect to Open Library."
    )

    fallback.enrich.side_effect = BookInformationServiceError(
        "Could not connect to Google Books."
    )

    service = FallbackBookInformationService(
        primary=primary,
        fallback=fallback,
    )

    book = BookInput(
        title="Charlotte's Web",
    )

    with pytest.raises(
        BookInformationServiceError,
        match="Could not connect to Google Books",
    ):
        service.enrich(book)

    primary.enrich.assert_called_once_with(book)
    fallback.enrich.assert_called_once_with(book)