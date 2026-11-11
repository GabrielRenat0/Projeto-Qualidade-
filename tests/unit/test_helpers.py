"""Unit tests for ``helpers.py``, covering the error paths the 20 test cases never reach."""

from pathlib import Path

import pytest
import requests

from helpers import assert_fields, assert_json, load_payloads

pytestmark = pytest.mark.unit


def write_payloads(folder: Path, content: str) -> Path:
    """Write ``content`` to a test data file in ``folder`` and return its path."""
    path = folder / "payloads.json"
    path.write_text(content, encoding="utf-8")
    return path


def make_response(body: bytes, content_type: str | None) -> requests.Response:
    """Return an offline response with ``body`` and, when given, a Content-Type."""
    response = requests.Response()
    response.status_code = 200
    if content_type is not None:
        response.headers["Content-Type"] = content_type
    response._content = body
    return response


# load_payloads


def test_load_payloads_reads_a_json_object(tmp_path):
    path = write_payloads(tmp_path, '{"valid_post": {"title": "foo"}}')

    assert load_payloads(path) == {"valid_post": {"title": "foo"}}


def test_load_payloads_fails_when_the_file_does_not_exist(tmp_path):
    missing = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError, match="Test data file not found") as error:
        load_payloads(missing)

    assert str(missing.resolve()) in str(error.value)


def test_load_payloads_fails_with_the_position_of_invalid_json(tmp_path):
    path = write_payloads(tmp_path, '{"title": }')

    with pytest.raises(ValueError, match="Invalid JSON") as error:
        load_payloads(path)

    assert "(line 1, column 11): Expecting value" in str(error.value)


def test_load_payloads_fails_when_the_json_is_not_an_object(tmp_path):
    path = write_payloads(tmp_path, '[{"title": "foo"}]')

    with pytest.raises(ValueError, match="must be a JSON object at the top level"):
        load_payloads(path)


def test_load_payloads_returns_an_independent_copy_on_each_call(tmp_path):
    path = write_payloads(tmp_path, '{"valid_post": {"title": "foo"}}')

    first = load_payloads(path)
    first["valid_post"]["title"] = "changed by a test"

    assert load_payloads(path)["valid_post"]["title"] == "foo"


# assert_fields


def test_assert_fields_passes_when_every_field_is_present():
    assert_fields({"id": 1, "title": "foo"}, ["id", "title"])


def test_assert_fields_lists_every_missing_field():
    with pytest.raises(AssertionError) as error:
        assert_fields({"id": 1, "title": "foo"}, ["id", "body", "userId"])

    message = str(error.value)
    assert "Missing fields ['body', 'userId']" in message
    assert "available fields: ['id', 'title']" in message


def test_assert_fields_rejects_an_item_that_is_not_an_object():
    with pytest.raises(AssertionError, match="Expected a JSON object, got list"):
        assert_fields([{"id": 1}], ["id"])


# assert_json


def test_assert_json_returns_the_parsed_body():
    response = make_response(b'{"id": 1}', "application/json; charset=utf-8")

    assert assert_json(response) == {"id": 1}


def test_assert_json_rejects_a_response_that_is_not_json():
    response = make_response(b"<h1>Not Found</h1>", "text/html; charset=utf-8")

    with pytest.raises(AssertionError, match="Expected a JSON response") as error:
        assert_json(response)

    assert "'text/html; charset=utf-8'" in str(error.value)


def test_assert_json_rejects_a_response_without_content_type():
    response = make_response(b'{"id": 1}', None)

    with pytest.raises(AssertionError, match="got Content-Type ''"):
        assert_json(response)
