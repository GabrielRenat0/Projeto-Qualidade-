"""API tests with invalid or unexpected input data (TC-011 to TC-020)."""

from http import HTTPStatus

import pytest

from helpers import assert_json

pytestmark = pytest.mark.invalid


def test_tc016_create_empty_post(api, payloads):
    """TC-016 - POST /posts with an empty body should return 201, showing the API does not validate the payload."""
    post_payload = payloads["empty_post"]
    response = api.post("/posts", json=post_payload)

    # Observed mock behavior: it returns 201 for an empty body; a real API would typically return 400.
    assert response.status_code == HTTPStatus.CREATED
    created_post = assert_json(response)

    assert "id" in created_post
    assert isinstance(created_post["id"], int)

    assert "title" not in created_post
    assert "body" not in created_post
    assert "userId" not in created_post


def test_tc017_create_post_with_invalid_types(api, payloads):
    """TC-017 - POST /posts with wrong field types should return 201, showing the API does not enforce a schema."""
    post_payload = payloads["post_with_invalid_types"]
    response = api.post("/posts", json=post_payload)

    # Observed mock behavior: it returns 201 for wrong field types; a real API would typically return 400.
    assert response.status_code == HTTPStatus.CREATED
    created_post = assert_json(response)

    assert "id" in created_post
    assert isinstance(created_post["id"], int)

    assert created_post["title"] == post_payload["title"]
    assert isinstance(created_post["title"], int)

    assert created_post["userId"] == post_payload["userId"]
    assert isinstance(created_post["userId"], str)


def test_tc018_update_nonexistent_post(api, payloads):
    """TC-018 - PUT /posts/999999 should return 500, showing the mock crashes when updating a nonexistent resource."""

    post_id = payloads["nonexistent_post_id"]
    put_payload = payloads["update_nonexistent_post"]

    response = api.put(f"/posts/{post_id}", json=put_payload)

    # Observed mock behavior: it returns 500 for a nonexistent post; a real API would typically return 404.
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert "text/html" in response.headers["Content-Type"]
