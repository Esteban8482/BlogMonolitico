from unittest.mock import patch, Mock
from routes import user_route
from datetime import datetime


def mock_current_user(client, user_id=1):
    # Simula usuario autenticado
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    client.application.view_functions["user.profile"] = user_route.profile.__wrapped__


def mock_request_res(status_code=200, json=None):
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {
        "profile_user": {
            "id": "1",
            "username": "juan",
            "bio": "Hola",
            "created_at": "2025-01-01",
        },
    }

    return mock_response


@patch("routes.user_route.requests")
@patch("routes.user_route.get_user_posts")
@patch("routes.user_route.current_user")
def test_get_user_profile(mock_current_user, mock_get_posts, mock_req, client):
    mock_current_user(client, user_id=1)
    remove_decorators(client)

    mock_res_user = {
        "profile_user": {
            "id": "1",
            "username": "juan",
            "bio": "Hola",
            "created_at": "2025-01-01",
        }
    }

    mock_current_user.return_value = type("User", (), {"id": 1})()
    mock_req.get.return_value = mock_request_res(json=mock_res_user)

    response = client.get("/u/juan")
    assert response.status_code == 200
    assert "Hola" in response.get_data(as_text=True)
