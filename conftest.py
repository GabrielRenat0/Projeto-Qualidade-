from collections.abc import Iterator
from typing import Any

import pytest
import requests

from helpers import load_payloads

BASE_URL = "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_HEADERS = {"Content-Type": "application/json"}


class APIClient:
    """HTTP client bound to the API base URL with a default timeout."""

    def __init__(self, session: requests.Session, base_url: str, timeout: float) -> None:
        self.session = session
        self.base_url = base_url
        self.timeout = timeout

    def _request(self, method: str, route: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{route}", **kwargs)

    def get(self, route: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", route, **kwargs)

    def post(self, route: str, **kwargs: Any) -> requests.Response:
        return self._request("POST", route, **kwargs)

    def put(self, route: str, **kwargs: Any) -> requests.Response:
        return self._request("PUT", route, **kwargs)

    def patch(self, route: str, **kwargs: Any) -> requests.Response:
        return self._request("PATCH", route, **kwargs)

    def delete(self, route: str, **kwargs: Any) -> requests.Response:
        return self._request("DELETE", route, **kwargs)


@pytest.fixture(scope="session")
def api() -> Iterator[APIClient]:
    """Session-wide API client; the HTTP session is closed after the run."""
    with requests.Session() as session:
        session.headers.update(DEFAULT_HEADERS)
        yield APIClient(session, BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS)


@pytest.fixture
def payloads() -> dict[str, Any]:
    """Fresh copy of data/payloads.json for each test, so tests never share data."""
    return load_payloads()
