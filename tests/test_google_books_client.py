import httpx
import pytest
import time

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)
from bookmatch.services.google_books_client import (
    GoogleBooksClient,
)


def test_get_adds_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    class MockResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {"items": []}

    def mock_get(url, **kwargs):
        captured["url"] = url
        captured["params"] = kwargs["params"]
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    client = GoogleBooksClient(
        api_key="test-key",
    )

    result = client.get(
        {"q": 'intitle:"A Wrinkle in Time"'}
    )

    assert result == {"items": []}
    assert captured["url"] == client.BASE_URL
    assert captured["params"]["key"] == "test-key"
    assert (
        captured["params"]["q"]
        == 'intitle:"A Wrinkle in Time"'
    )


def test_timeout_raises_service_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_get(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "get", mock_get)

    client = GoogleBooksClient(
        api_key="test-key",
    )

    with pytest.raises(
        BookInformationServiceError,
        match="timed out",
    ):
        client.get({"q": "test"})


def test_request_error_raises_service_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_get(*args, **kwargs):
        raise httpx.RequestError("connection failed")

    monkeypatch.setattr(httpx, "get", mock_get)

    client = GoogleBooksClient(
        api_key="test-key",
    )

    with pytest.raises(
        BookInformationServiceError,
        match="Could not connect",
    ):
        client.get({"q": "test"})


def test_non_429_http_error_raises_service_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = httpx.Request(
        "GET",
        "https://example.com",
    )

    response = httpx.Response(
        503,
        request=request,
    )

    def mock_get(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "get", mock_get)

    client = GoogleBooksClient(
        api_key="test-key",
    )

    with pytest.raises(
        BookInformationServiceError,
        match="HTTP 503",
    ):
        client.get({"q": "test"})


def test_429_is_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = httpx.Request(
        "GET",
        "https://example.com",
    )

    rate_limit_response = httpx.Response(
        429,
        headers={"Retry-After": "0"},
        request=request,
    )

    success_response = httpx.Response(
        200,
        json={"items": []},
        request=request,
    )

    responses = iter(
        [
            rate_limit_response,
            success_response,
        ]
    )

    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: next(responses),
    )

    monkeypatch.setattr(
        time,
        "sleep",
        lambda seconds: None,
    )

    client = GoogleBooksClient(
        api_key="test-key",
    )

    result = client.get({"q": "test"})

    assert result == {"items": []}