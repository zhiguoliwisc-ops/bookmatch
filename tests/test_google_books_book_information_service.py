from unittest.mock import Mock

import pytest

from bookmatch.models.book import BookInput
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)
from bookmatch.services.google_books_book_information_service import (
    GoogleBooksBookInformationService,
)


def test_enrich_by_isbn_returns_enriched_book() -> None:
    response = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": (
                        "A story about a pig named Wilbur."
                    ),
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780064400558",
                        }
                    ],
                }
            }
        ]
    }

    service = GoogleBooksBookInformationService(
        api_key="test-api-key",
    )

    service.client = Mock()
    service.client.get.return_value = response

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    result = service.enrich(book)

    service.client.get.assert_called_once_with(
        {
            "q": "isbn:9780064400558",
        }
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.publication_date == "1952-10-15"
    assert result.isbn == "9780064400558"
    assert result.description == (
        "A story about a pig named Wilbur."
    )
    assert result.source == "Google Books"


def test_enrich_by_isbn_raises_error_when_book_not_found() -> None:
    response = {
        "totalItems": 0,
    }

    service = GoogleBooksBookInformationService(
        api_key="test-api-key",
    )

    service.client = Mock()
    service.client.get.return_value = response

    book = BookInput(
        title="Some Unknown Book",
        isbn="0000000000000",
    )

    with pytest.raises(
        BookInformationServiceError,
        match="Could not find book",
    ):
        service.enrich(book)

        assert service.client.get.call_count == 2

        service.client.get.assert_any_call(
            {
                "q": "isbn:0000000000000",
            }
        )

        service.client.get.assert_any_call(
            {
                "q": 'intitle:"Some Unknown Book"',
            }
        )


def test_enrich_by_title_returns_enriched_book() -> None:
    response = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": (
                        "A story about a pig named Wilbur."
                    ),
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780064400558",
                        }
                    ],
                }
            }
        ]
    }

    service = GoogleBooksBookInformationService(
        api_key="test-api-key",
    )

    service.client = Mock()
    service.client.get.return_value = response

    book = BookInput(
        title="Charlotte's Web",
    )

    result = service.enrich(book)

    service.client.get.assert_called_once_with(
        {
            "q": 'intitle:"Charlotte\'s Web"',
        }
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.description == (
        "A story about a pig named Wilbur."
    )
    assert result.source == "Google Books"


def test_enrich_by_title_and_author_returns_enriched_book() -> None:
    response = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": (
                        "A story about a pig named Wilbur."
                    ),
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780064400558",
                        }
                    ],
                }
            }
        ]
    }

    service = GoogleBooksBookInformationService(
        api_key="test-api-key",
    )

    service.client = Mock()
    service.client.get.return_value = response

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    result = service.enrich(book)

    service.client.get.assert_called_once_with(
        {
            "q": (
                'intitle:"Charlotte\'s Web"'
                '+inauthor:"E. B. White"'
            ),
        }
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.description == (
        "A story about a pig named Wilbur."
    )
    assert result.source == "Google Books"