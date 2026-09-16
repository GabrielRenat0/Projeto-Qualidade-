"""Happy-path API tests with valid input data (TC-001 to TC-010)."""

from http import HTTPStatus

import pytest

from helpers import assert_fields, assert_json

pytestmark = pytest.mark.valid

EXPECTED_POST_COUNT = 100
POST_FIELDS = ("id", "userId", "title", "body")


def test_tc001_list_all_posts(api):
    """TC-001 - GET /posts should return all 100 posts with the post schema."""
    response = api.get("/posts")

    assert response.status_code == HTTPStatus.OK
    posts = assert_json(response)
    assert isinstance(posts, list)
    assert len(posts) == EXPECTED_POST_COUNT
    for post in posts:
        assert_fields(post, POST_FIELDS)


@pytest.mark.parametrize("bound", ["lower_bound", "upper_bound"])
def test_tc002_get_post_at_valid_boundaries(api, payloads, bound):
    """TC-002 - GET /posts/{id} should return the post at ID boundaries 1 and 100."""
    post_id = payloads["valid_boundary_post_ids"][bound]

    response = api.get(f"/posts/{post_id}")

    assert response.status_code == HTTPStatus.OK
    post = assert_json(response)
    assert post["id"] == post_id
    assert_fields(post, POST_FIELDS)
