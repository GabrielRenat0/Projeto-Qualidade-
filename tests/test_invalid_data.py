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