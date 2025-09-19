from unittest.mock import patch
from routes import user_route
from datetime import datetime


def mock_current_user(client, user_id=1):
    # Simula usuario autenticado
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    client.application.view_functions["user.profile"] = user_route.profile.__wrapped__


@patch("routes.user_route.get_user_or_404")
@patch("routes.user_route.get_user_posts")
def test_get_user_profile(mock_get_posts, mock_get_user, client):
    mock_current_user(client, user_id=1)
    remove_decorators(client)

    mock_get_user.return_value = type(
        "User",
        (),
        {
            "id": 1,
            "username": "juan",
            "bio": "Hola",
            "created_at": datetime(2025, 1, 1),
        },
    )()

    mock_get_posts.return_value = [
        type(
            "Post",
            (),
            {
                "id": 1,
                "created_at": datetime(2025, 1, 1),
                "title": "Post de prueba",
                "content": "Contenido de prueba",
            },
        )()
    ]

    response = client.get("/u/juan")
    assert response.status_code == 200
    assert "Hola" in response.get_data(as_text=True)


@patch("routes.user_route.get_user_or_404")
@patch("routes.user_route.get_user_posts")
@patch("routes.user_route.is_user_owner")
def test_get_user_profile_not_owner(
    mock_is_owner, mock_get_posts, mock_get_user, client
):
    mock_current_user(client, user_id=2)
    remove_decorators(client)

    mock_is_owner.return_value = False
    mock_get_user.return_value = type(
        "User",
        (),
        {
            "id": 1,
            "username": "juan",
            "bio": "Hola",
            "created_at": datetime(2025, 1, 1),
        },
    )()

    mock_get_posts.return_value = [
        type(
            "Post",
            (),
            {
                "id": 1,
                "created_at": datetime(2025, 1, 1),
                "title": "Post de prueba",
                "content": "Contenido de prueba",
            },
        )()
    ]

    response = client.get("/u/juan")
    assert response.status_code == 200  # un usuario puede ver perfiles de otros


@patch("routes.user_route.get_user_posts")
@patch("routes.user_route.update_user_bio")
@patch("routes.user_route.get_user_or_404")
@patch("routes.user_route.is_user_owner")
def test_update_user_bio_success(
    mock_is_owner, mock_get_user, mock_update, mock_get_posts, client
):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_user = type(
        "User",
        (),
        {
            "id": 1,
            "username": "juan",
            "bio": "Hola",
            "created_at": datetime(2025, 1, 1),
        },
    )()
    mock_is_owner.return_value = True
    mock_get_user.return_value = mock_user
    mock_get_posts.return_value = []

    response = client.post("/u/juan", data={"bio": "Nuevo bio"}, follow_redirects=True)

    assert response.status_code == 200
    mock_update.assert_called_once_with(mock_user, "Nuevo bio")


@patch("routes.user_route.get_user_posts")
@patch("routes.user_route.update_user_bio")
@patch("routes.user_route.get_user_or_404")
@patch("routes.user_route.is_user_owner")
def test_update_user_bio_not_owner(
    mock_is_owner, mock_get_user, mock_update, mock_get_posts, client
):
    remove_decorators(client)
    mock_current_user(client, user_id=2)

    mock_user = type(
        "User",
        (),
        {
            "id": 1,
            "username": "juan",
            "bio": "Hola",
            "created_at": datetime(2025, 1, 1),
        },
    )()
    mock_is_owner.return_value = False
    mock_get_user.return_value = mock_user
    mock_get_posts.return_value = []

    response = client.post("/u/juan", data={"bio": "Nuevo bio"}, follow_redirects=True)

    assert response.status_code == 403
    mock_update.assert_not_called()
