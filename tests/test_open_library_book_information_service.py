import pytest

from bookmatch.models.book import BookInput
from bookmatch.services.exceptions import BookNotFoundError
from bookmatch.services.open_library_book_information_service import (
    OpenLibraryBookInformationService,
)


def test_enrich_by_isbn(monkeypatch):
    def mock_get(url, **kwargs):
        class MockResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "title": "Charlotte's Web",
                    "description": {
                        "value": "A story about a pig and a spider."
                    },
                }

        return MockResponse()

    monkeypatch.setattr("httpx.get", mock_get)

    service = OpenLibraryBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
        isbn="9780064400558",
    )

    result = service.enrich(book)

    assert result.title == "Charlotte's Web"
    assert result.isbn == "9780064400558"
    assert result.description == "A story about a pig and a spider."
    assert result.source == "Open Library"


def test_fallback_to_title_search_when_isbn_not_found(monkeypatch):
    call_count = 0

    def mock_get(url, **kwargs):
        nonlocal call_count
        call_count += 1

        class MockResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data

            def raise_for_status(self):
                pass

            def json(self):
                return self._data

        if call_count == 1:
            return MockResponse(404, {})

        return MockResponse(
            200,
            {
                "docs": [
                    {
                        "title": "Charlotte's Web",
                        "author_name": ["E. B. White"],
                        "first_publish_year": 1952,
                        "isbn": ["9780064400558"],
                    }
                ]
            },
        )

    monkeypatch.setattr("httpx.get", mock_get)

    service = OpenLibraryBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="invalid-isbn",
    )

    result = service.enrich(book)

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.publication_date == "1952"
    assert result.isbn == "9780064400558"


def test_enrich_by_title_and_author(monkeypatch):
    def mock_get(url, **kwargs):
        class MockResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "docs": [
                        {
                            "title": "Matilda",
                            "author_name": ["Roald Dahl"],
                            "first_publish_year": 1988,
                            "isbn": ["9780142410370"],
                        }
                    ]
                }

        return MockResponse()

    monkeypatch.setattr("httpx.get", mock_get)

    service = OpenLibraryBookInformationService()

    book = BookInput(
        title="Matilda",
        author="Roald Dahl",
    )

    result = service.enrich(book)

    assert result.title == "Matilda"
    assert result.author == "Roald Dahl"
    assert result.publication_date == "1988"


def test_raise_error_when_book_is_not_found(monkeypatch):
    def mock_get(url, **kwargs):
        class MockResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "docs": []
                }

        return MockResponse()

    monkeypatch.setattr("httpx.get", mock_get)

    service = OpenLibraryBookInformationService()

    book = BookInput(
        title="A Completely Unknown Book",
    )

    with pytest.raises(BookNotFoundError):
        service.enrich(book)