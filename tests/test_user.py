from unittest.mock import patch
from routes import user_route
from dtos import UserDto, PostDto
from datetime import datetime


def mock_current_user(client, user_id=1):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    client.application.view_functions["user.profile"] = user_route.profile.__wrapped__


@patch("routes.user_route.get_user_profile")
@patch("routes.user_route.get_user_posts")
@patch("routes.user_route.current_user")
def test_get_user_profile_success(
    mock_current_user_func, mock_get_posts, mock_get_user, client
):
    mock_current_user(client, user_id=1)
    remove_decorators(client)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()

    mock_get_user.return_value = UserDto(
        id="1",
        username="juan",
        bio="Hola",
        created_at=datetime(2025, 1, 1),
    )

    mock_get_posts.return_value = [
        PostDto(
            id="p1",
            title="Post 1",
            content="Contenido",
            created_at=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
            user_id="1",
            username="juan",
        )
    ]

    response = client.get("/u/juan")
    assert response.status_code == 200
    assert "Hola" in response.get_data(as_text=True)
    assert "Post 1" in response.get_data(as_text=True)


@patch("routes.user_route.update_user_profile")
@patch("routes.user_route.current_user")
def test_post_user_profile_success(mock_current_user_func, mock_update_user, client):
    mock_current_user_func.return_value = type("User", (), {"id": 1})()

    mock_update_user.return_value = UserDto(
        id="1",
        username="juan",
        bio="Nueva bio",
        created_at=datetime(2025, 1, 1),
    )
    response = client.post("/u/juan", data={"bio": "Nueva bio"})
    assert response.status_code == 302
    assert "/u/juan" in response.headers["Location"]


@patch("routes.user_route.get_user_profile")
@patch("routes.user_route.current_user")
def test_get_user_profile_failure(mock_current_user_func, mock_get_user, client):
    mock_current_user(client, user_id=1)
    remove_decorators(client)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_get_user.return_value = None  # Simula fallo

    response = client.get("/u/juan")
    assert response.status_code == 400


@patch("routes.user_route.update_user_profile")
@patch("routes.user_route.current_user")
def test_post_user_profile_failure(mock_current_user_func, mock_update_user, client):
    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_update_user.return_value = None  # Simula fallo

    response = client.post("/u/juan", data={"bio": "Nueva bio"})
    assert response.status_code == 302
    assert "/u/juan" in response.headers["Location"]
