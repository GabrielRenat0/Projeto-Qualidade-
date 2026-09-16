"""Happy-path API tests with valid input data (TC-001 to TC-010)."""

from http import HTTPStatus

import pytest

from helpers import assert_fields, assert_json

pytestmark = pytest.mark.valid

EXPECTED_POST_COUNT = 100
POST_FIELDS = ("id", "userId", "title", "body")
POSTS_PER_USER = 10
COMMENT_FIELDS = ("postId", "id", "name", "email", "body")
COMMENTS_PER_POST = 5


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


def test_tc003_filter_posts_by_user_id(api, payloads):
    """TC-003 - GET /posts?userId=1 should return only the 10 posts of user 1."""
    user_filter = payloads["user_posts_filter"]

    response = api.get("/posts", params=user_filter)

    assert response.status_code == HTTPStatus.OK
    posts = assert_json(response)
    assert isinstance(posts, list)
    assert len(posts) == POSTS_PER_USER
    posts_from_other_users = [
        post["id"] for post in posts if post["userId"] != user_filter["userId"]
    ]
    assert not posts_from_other_users


def test_tc004_list_comments_of_post(api, payloads):
    """TC-004 - GET /posts/1/comments should return 5 comments with valid emails."""
    post_id = payloads["post_id_with_comments"]

    response = api.get(f"/posts/{post_id}/comments")

    assert response.status_code == HTTPStatus.OK
    comments = assert_json(response)
    assert isinstance(comments, list)
    assert len(comments) == COMMENTS_PER_POST
    for comment in comments:
        assert_fields(comment, COMMENT_FIELDS)
    comments_from_other_posts = [
        comment["id"] for comment in comments if comment["postId"] != post_id
    ]
    assert not comments_from_other_posts
    comments_with_invalid_email = [
        comment["id"] for comment in comments if "@" not in comment["email"]
    ]
    assert not comments_with_invalid_email
