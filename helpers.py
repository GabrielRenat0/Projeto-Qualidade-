import copy
import json
from functools import cache
from pathlib import Path
from typing import Any

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


def assert_campos(objeto, campos):
    for campo in campos:
        assert campo in objeto, f"Campo '{campo}' não encontrado no objeto"

def assert_json(resposta):
    assert "application/json" in resposta.headers.get("Content-Type", ""), "Response is not JSON"
    return resposta.json()

