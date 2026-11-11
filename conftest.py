from collections.abc import Iterator
import os
from typing import Any

import pytest
import requests

from helpers import load_payloads
from reporting import GROUP_HEADER_CELL, ReportSummary, group_cell, report_title

BASE_URL = os.environ.get("API_BASE_URL") or "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_HEADERS = {"Content-Type": "application/json"}

# The report logic lives in reporting.py; these hooks only hand pytest data to it.
_REPORT_SUMMARY = ReportSummary()


def pytest_html_report_title(report) -> None:
    """Give the single generated report a title that describes its scope."""
    report.title = report_title()


def pytest_html_results_table_header(cells: list[str]) -> None:
    """Add a visible group column to the pytest-html results table."""
    cells.insert(1, GROUP_HEADER_CELL)


def pytest_html_results_table_row(report, cells: list[str]) -> None:
    """Label every test result with its group: an integrante or the unit tests."""
    cells.insert(1, group_cell(report.nodeid))


def pytest_runtest_logreport(report) -> None:
    """Collect the outcomes of each group for the report summary."""
    if report.when == "call":
        _REPORT_SUMMARY.record(report.nodeid, report.outcome)


def pytest_html_results_summary(prefix: list[str], session) -> None:
    """Add a concise breakdown of the consolidated report to its summary."""
    prefix.extend(_REPORT_SUMMARY.html_lines())


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
