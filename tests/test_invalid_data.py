"""API tests with invalid or unexpected input data (TC-011 to TC-020)."""

from http import HTTPStatus

import pytest

from helpers import assert_json

pytestmark = pytest.mark.invalid


@pytest.mark.parametrize(
    "bound", ["below_lower_bound", "above_upper_bound", "far_above_upper_bound"]
)
def test_tc011_get_post_outside_valid_id_range(api, payloads, bound):
    """TC-011 - GET /posts/{id} outside the valid 1-100 range should return 404."""
    post_id = payloads["out_of_range_post_ids"][bound]

    response = api.get(f"/posts/{post_id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = assert_json(response)
    assert body == {}


def test_tc012_get_post_with_non_numeric_id(api, payloads):
    """TC-012 - GET /posts/{id} with a non-numeric ID should return 404."""
    post_id = payloads["invalid_type_post_id"]

    response = api.get(f"/posts/{post_id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = assert_json(response)
    assert body == {}


def test_tc013_get_nonexistent_route(api, payloads):
    """TC-013 - GET /nonexistent-resource should return 404 for an unknown route."""
    route = payloads["nonexistent_route"]

    response = api.get(route)

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = assert_json(response)
    assert body == {}


def test_tc014_filter_posts_by_nonexistent_user(api, payloads):
    """TC-014 - GET /posts?userId=9999 should return 200 and an empty list."""
    user_filter = payloads["nonexistent_user_filter"]

    response = api.get("/posts", params=user_filter)

    assert response.status_code == HTTPStatus.OK
    posts = assert_json(response)
    assert posts == []


def test_tc015_filter_comments_by_negative_post_id(api, payloads):
    """TC-015 - GET /comments?postId=-1 should return 200 and an empty list."""
    comment_filter = payloads["negative_comment_filter"]

    response = api.get("/comments", params=comment_filter)

    assert response.status_code == HTTPStatus.OK
    comments = assert_json(response)
    assert comments == []


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


def test_tc019_create_post_with_malformed_json(api, payloads):
    """TC-019 - POST /posts with a malformed JSON body should return 500, showing the mock does not handle parse errors."""
    malformed_body = payloads["malformed_json"]

    response = api.post("/posts", data=malformed_body)

    # Observed mock behavior: it returns 500 for a malformed JSON body; a real API would typically return 400.
    # The error only happens because the api fixture sends Content-Type: application/json;
    # without that header the mock accepts the body and returns 201.
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "text/html" in response.headers["Content-Type"]
    assert "SyntaxError" in response.text


def test_tc020_get_post_after_delete(api, payloads):
    """TC-020 - GET /posts/1 after DELETE /posts/1 should still return 200, showing the mock does not persist deletions."""
    post_id = payloads["post_id_to_delete"]

    delete_response = api.delete(f"/posts/{post_id}")

    assert delete_response.status_code == HTTPStatus.OK

    get_response = api.get(f"/posts/{post_id}")

    # Observed mock behavior: the deleted post is still returned with 200; a real API would typically return 404.
    assert get_response.status_code == HTTPStatus.OK
    deleted_post = assert_json(get_response)
    assert deleted_post["id"] == post_id
