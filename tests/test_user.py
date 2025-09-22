from unittest.mock import patch, Mock
from routes import user_route


def mock_current_user(client, user_id=1):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    client.application.view_functions["user.profile"] = user_route.profile.__wrapped__


def mock_request_res_user():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "id": "1",
            "username": "juan",
            "bio": "Hola",
            "created_at": "2025-01-01",
        }
    }
    return mock_response


def mock_request_res_posts():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "posts": [
            {
                "id": "p1",
                "title": "Post 1",
                "content": "Contenido",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-01",
                "user_id": "1",
                "username": "juan",
            }
        ]
    }
    return mock_response


@patch("routes.user_route.requests")
@patch("routes.user_route.current_user")
def test_get_user_profile(mock_current_user_func, mock_requests, client):
    mock_current_user(client, user_id=1)
    remove_decorators(client)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_requests.get.side_effect = [mock_request_res_user(), mock_request_res_posts()]

    response = client.get("/u/juan")
    assert response.status_code == 200
    assert "Hola" in response.get_data(as_text=True)
    assert "Post 1" in response.get_data(as_text=True)


@patch("routes.user_route.requests")
@patch("routes.user_route.current_user")
def test_post_user_profile(mock_current_user_func, mock_requests, client):
    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_requests.post.return_value = Mock(status_code=200)

    response = client.post("/u/juan", data={"bio": "Nueva bio"})
    assert response.status_code == 302  # redirección
