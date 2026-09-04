from unittest.mock import Mock, patch

from bookmatch.models.book import BookInput
from bookmatch.services.google_books_book_information_service import (
    GoogleBooksBookInformationService,
)

import pytest

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)

def test_enrich_by_isbn_returns_enriched_book() -> None:
    response = Mock()

    response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": "A story about a pig named Wilbur.",
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

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.enrich(book)

    mock_get.assert_called_once_with(
        service.BASE_URL,
        params={
            "q": "isbn:9780064400558",
        },
        timeout=10.0,
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.publication_date == "1952-10-15"
    assert result.isbn == "9780064400558"
    assert result.description == "A story about a pig named Wilbur."
    assert result.source == "Google Books"

def test_enrich_by_isbn_raises_error_when_book_not_found() -> None:
    response = Mock()

    response.json.return_value = {
        "totalItems": 0,
    }

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Some Unknown Book",
        isbn="0000000000000",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ):
        with pytest.raises(
            BookInformationServiceError,
            match="Could not find book",
        ):
            service.enrich(book)

def test_enrich_by_title_returns_enriched_book() -> None:
    response = Mock()

    response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": "A story about a pig named Wilbur.",
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

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.enrich(book)

    mock_get.assert_called_once_with(
        service.BASE_URL,
        params={
            "q": 'intitle:"Charlotte\'s Web"',
        },
        timeout=10.0,
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.description == "A story about a pig named Wilbur."
    assert result.source == "Google Books"

def test_enrich_by_title_and_author_returns_enriched_book() -> None:
    response = Mock()

    response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": "A story about a pig named Wilbur.",
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

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.enrich(book)

    mock_get.assert_called_once_with(
        service.BASE_URL,
        params={
            "q": 'intitle:"Charlotte\'s Web"+inauthor:"E. B. White"',
        },
        timeout=10.0,
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.description == "A story about a pig named Wilbur."
    assert result.source == "Google Books"