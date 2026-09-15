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
