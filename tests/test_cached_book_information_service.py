
from unittest.mock import Mock

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.services.cached_book_information_service import (
    CachedBookInformationService,
)


def test_returns_cached_result_without_calling_underlying_service() -> None:
    underlying_service = Mock()

    enriched_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="A story about a pig and a spider.",
        source="Google Books",
    )

    underlying_service.enrich.return_value = enriched_book

    service = CachedBookInformationService(
        underlying_service,
    )

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    first_result = service.enrich(book)
    second_result = service.enrich(book)

    assert first_result == enriched_book
    assert second_result == enriched_book
    assert underlying_service.enrich.call_count == 1

def test_uses_title_and_author_as_cache_key_when_isbn_is_missing() -> None:
    underlying_service = Mock()

    enriched_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn=None,
        description="A story about a pig and a spider.",
        source="Google Books",
    )

    underlying_service.enrich.return_value = enriched_book

    service = CachedBookInformationService(
        underlying_service,
    )

    first_book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    second_book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    first_result = service.enrich(first_book)
    second_result = service.enrich(second_book)

    assert first_result == enriched_book
    assert second_result == enriched_book
    assert underlying_service.enrich.call_count == 1

def test_does_not_share_cache_between_different_authors() -> None:
    underlying_service = Mock()

    first_enriched_book = EnrichedBook(
        title="The Crossing",
        author="Author A",
        publication_date="2020",
        isbn=None,
        description="Description A",
        source="Google Books",
    )

    second_enriched_book = EnrichedBook(
        title="The Crossing",
        author="Author B",
        publication_date="2021",
        isbn=None,
        description="Description B",
        source="Google Books",
    )

    underlying_service.enrich.side_effect = [
        first_enriched_book,
        second_enriched_book,
    ]

    service = CachedBookInformationService(
        underlying_service,
    )

    first_book = BookInput(
        title="The Crossing",
        author="Author A",
    )

    second_book = BookInput(
        title="The Crossing",
        author="Author B",
    )

    first_result = service.enrich(first_book)
    second_result = service.enrich(second_book)

    assert first_result == first_enriched_book
    assert second_result == second_enriched_book
    assert underlying_service.enrich.call_count == 2

def test_returns_cached_value_after_underlying_service_changes() -> None:
    underlying_service = Mock()

    first_enriched_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="First result.",
        source="Google Books",
    )

    second_enriched_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="Second result.",
        source="Google Books",
    )

    underlying_service.enrich.side_effect = [
        first_enriched_book,
        second_enriched_book,
    ]

    service = CachedBookInformationService(
        underlying_service,
    )

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    first_result = service.enrich(book)

    # Change what the underlying service would return.
    underlying_service.enrich.return_value = second_enriched_book

    second_result = service.enrich(book)

    assert first_result == first_enriched_book
    assert second_result == first_enriched_book
    assert underlying_service.enrich.call_count == 1

