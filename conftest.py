from collections.abc import Iterator
from collections import Counter, defaultdict
from html import escape
import re
from typing import Any

import pytest
import requests

from helpers import load_payloads

BASE_URL = "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_HEADERS = {"Content-Type": "application/json"}

_REPORT_GROUPS = {
    "Integrante A": (1, 5),
    "Integrante B": (6, 10),
    "Integrante C": (11, 15),
    "Integrante D": (16, 20),
}
_REPORT_COUNTS: defaultdict[str, Counter[str]] = defaultdict(Counter)


def _report_group(nodeid: str) -> str:
    """Return the integrante responsible for the test case in ``nodeid``."""
    match = re.search(r"tc[-_]?(\d{3})", nodeid, flags=re.IGNORECASE)
    if match:
        test_case = int(match.group(1))
        for integrante, (first_case, last_case) in _REPORT_GROUPS.items():
            if first_case <= test_case <= last_case:
                return integrante
    return "Não classificado"


def pytest_html_report_title(report) -> None:
    """Give the single generated report a title that describes its scope."""
    first_case = min(first for first, _ in _REPORT_GROUPS.values())
    last_case = max(last for _, last in _REPORT_GROUPS.values())
    report.title = f"Relatório consolidado — TC-{first_case:03d} a TC-{last_case:03d}"


def pytest_html_results_table_header(cells: list[str]) -> None:
    """Add a visible integrante column to the pytest-html results table."""
    cells.insert(1, "<th>Integrante</th>")


def pytest_html_results_table_row(report, cells: list[str]) -> None:
    """Label every test result with the integrante responsible for its TC."""
    integrante = escape(_report_group(report.nodeid))
    cells.insert(1, f'<td class="col-integrante">{integrante}</td>')


def pytest_runtest_logreport(report) -> None:
    """Collect per-integrante outcomes for the report summary."""
    if report.when == "call":
        _REPORT_COUNTS[_report_group(report.nodeid)][report.outcome] += 1


def pytest_html_results_summary(prefix: list[str], session) -> None:
    """Add a concise breakdown of the consolidated report to its summary."""
    lines = [
        "<h3>Resultados por integrante</h3>",
        "<ul>",
    ]
    for integrante, (first_case, last_case) in _REPORT_GROUPS.items():
        counts = _REPORT_COUNTS.get(integrante, Counter())
        total = sum(counts.values())
        if not total:
            continue
        status = ", ".join(
            f"{amount} {outcome}"
            for outcome, amount in sorted(counts.items())
        )
        lines.append(
            f"<li><strong>{integrante}</strong> — "
            f"TC-{first_case:03d} a TC-{last_case:03d}: "
            f"{total} execuções ({escape(status)}).</li>"
        )
    lines.extend(["</ul>"])
    prefix.extend(lines)


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
