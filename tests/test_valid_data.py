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
USER_FIELDS = ("id", "name", "username", "email", "address", "company")
ADDRESS_FIELDS = ("street", "city", "zipcode", "geo")
GEO_FIELDS = ("lat", "lng")
COMPANY_FIELDS = ("name", "catchPhrase", "bs")


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


def test_tc005_get_user_with_nested_objects(api, payloads):
    """TC-005 - GET /users/1 should return nested address.geo and company objects."""
    user_id = payloads["existing_user_id"]

    response = api.get(f"/users/{user_id}")

    assert response.status_code == HTTPStatus.OK
    user = assert_json(response)
    assert_fields(user, USER_FIELDS)
    assert user["id"] == user_id
    assert_fields(user["address"], ADDRESS_FIELDS)
    assert_fields(user["company"], COMPANY_FIELDS)
    geo = user["address"]["geo"]
    assert_fields(geo, GEO_FIELDS)
    invalid_coordinates = [
        name for name in GEO_FIELDS if not isinstance(geo[name], str) or not geo[name]
    ]
    assert not invalid_coordinates


def test_tc006_filter_completed_todos(api):
    """TC-006 - GET /todos?completed=true should return only completed todos."""
    response = api.get("/todos", params={"completed": "true"})

    assert response.status_code == HTTPStatus.OK
    todos = assert_json(response)
    assert isinstance(todos, list)
    assert len(todos) > 0, "Expected at least one completed todo"
    incomplete_todos = [
        todo["id"] for todo in todos if todo["completed"] is not True
    ]
    assert not incomplete_todos


def test_tc007_create_post(api, payloads):
    """TC-007 - POST /posts with valid payload should return 201, an ID, and echo fields."""
    post_payload = payloads["valid_post"]

    response = api.post("/posts", json=post_payload)

    assert response.status_code == HTTPStatus.CREATED
    created_post = assert_json(response)
    
    # Valida que um ID foi gerado
    assert "id" in created_post
    assert isinstance(created_post["id"], int)
    
    # Valida que os campos enviados foram ecoados corretamente
    assert created_post["title"] == post_payload["title"]
    assert created_post["body"] == post_payload["body"]
    assert created_post["userId"] == post_payload["userId"]


def test_tc008_update_post(api, payloads):
    """TC-008 - PUT /posts/1 should update all fields and return 200."""
    put_payload = payloads["updated_post"]
    post_id = put_payload["id"]

    response = api.put(f"/posts/{post_id}", json=put_payload)

    assert response.status_code == HTTPStatus.OK
    updated_post = assert_json(response)
    
    assert updated_post["id"] == post_id
    assert updated_post["title"] == put_payload["title"]
    assert updated_post["body"] == put_payload["body"]
    assert updated_post["userId"] == put_payload["userId"]

