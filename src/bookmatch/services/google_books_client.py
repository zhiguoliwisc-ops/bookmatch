import time

import httpx

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)


class GoogleBooksClient:
    """HTTP client for the Google Books API."""

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    REQUEST_INTERVAL = 1.0

    def __init__(
        self,
        api_key: str,
    ) -> None:
        self.api_key = api_key
        self._next_allowed_request_time = 0.0

    def get(
        self,
        params: dict,
    ) -> dict:
        """Send a GET request to Google Books."""

        request_params = {
            **params,
            "key": self.api_key,
        }

        response = self._get_with_retry(
            self.BASE_URL,
            params=request_params,
        )

        return response.json()

    def _get_with_retry(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                self._throttle()

                response = httpx.get(
                    url,
                    timeout=10.0,
                    **kwargs,
                )

                response.raise_for_status()

                return response

            except httpx.TimeoutException as error:
                raise BookInformationServiceError(
                    "The request to Google Books timed out."
                ) from error

            except httpx.HTTPStatusError as error:
                if (
                    error.response.status_code == 429
                    and attempt < max_attempts - 1
                ):
                    retry_after = error.response.headers.get(
                        "Retry-After"
                    )

                    if retry_after is not None:
                        delay = float(retry_after)
                    else:
                        delay = 2**attempt

                    print(
                        "Google Books rate limit reached. "
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)
                    continue

                raise BookInformationServiceError(
                    f"Google Books returned HTTP "
                    f"{error.response.status_code}."
                ) from error

            except httpx.RequestError as error:
                raise BookInformationServiceError(
                    "Could not connect to Google Books."
                ) from error

        raise BookInformationServiceError(
            "Google Books request failed."
        )

    def _throttle(self) -> None:
        now = time.monotonic()

        if now < self._next_allowed_request_time:
            time.sleep(
                self._next_allowed_request_time - now
            )

        self._next_allowed_request_time = (
            time.monotonic()
            + self.REQUEST_INTERVAL
        )