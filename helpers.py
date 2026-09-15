import copy
import json
from collections.abc import Iterable
from functools import cache
from pathlib import Path
from typing import Any

import requests

PAYLOADS_PATH = Path(__file__).resolve().parent / "data" / "payloads.json"


def load_payloads(path: Path = PAYLOADS_PATH) -> dict[str, Any]:
    """Return an independent copy of the test data stored in ``path``."""
    # The cached dict is shared between calls, so callers only ever get a deep copy.
    return copy.deepcopy(_read_payloads(path))


@cache
def _read_payloads(path: Path) -> dict[str, Any]:
    """Read and parse the test data file once per run."""
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Test data file not found: {path.resolve()}") from None

    try:
        payloads = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {path.resolve()} "
            f"(line {error.lineno}, column {error.colno}): {error.msg}"
        ) from error

    if not isinstance(payloads, dict):
        raise ValueError(
            f"Test data in {path.resolve()} must be a JSON object at the top level"
        )

    return payloads


def assert_fields(item: dict[str, Any], fields: Iterable[str]) -> None:
    """Fail listing every expected field that is missing from ``item``."""
    assert isinstance(item, dict), f"Expected a JSON object, got {type(item).__name__}"

    missing = [field for field in fields if field not in item]
    assert not missing, f"Missing fields {missing}; available fields: {sorted(item)}"


def assert_json(response: requests.Response) -> Any:
    """Assert that the response declares a JSON body and return it parsed."""
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"Expected a JSON response, got Content-Type {content_type!r}"
    )

    return response.json()

