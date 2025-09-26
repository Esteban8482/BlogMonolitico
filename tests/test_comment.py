from unittest.mock import patch, Mock
from routes import comment_route
from datetime import datetime


def mock_current_user_session(client, user_id=1):
    # Simula usuario autenticado
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    # Reemplaza la vista decorada por la versión original sin decorador
    client.application.view_functions[
        "comment.add_comment"
    ] = comment_route.add_comment.__wrapped__
    client.application.view_functions[
        "comment.delete_comment"
    ] = comment_route.delete_comment.__wrapped__


@patch("routes.comment_route.requests")
@patch("routes.comment_route.create_comment")
@patch("routes.comment_route.current_user")
def test_add_comment_success(
    mock_current_user, mock_create_comment, mock_requests, client
):
    remove_decorators(client)
    mock_current_user_session(client, user_id=1)

    mock_current_user.return_value = type("User", (), {"id": 1})()
    mock_requests.get.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "post": {
                    "id": "123",
                    "title": "Test",
                    "content": "Contenido",
                    "created_at": "2025-09-21T00:00:00",
                    "updated_at": "2025-09-21T00:00:00",
                    "user_id": "1",
                    "username": "juan",
                }
            }
        ),
    )

    response = client.post(
        "/post/123/comment", data={"content": "Hola"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Comentario agregado" in response.get_data(as_text=True)
    mock_create_comment.assert_called_once_with("123", "Hola")


@patch("routes.comment_route.requests")
@patch("routes.comment_route.create_comment")
@patch("routes.comment_route.current_user")
def test_add_comment_empty(
    mock_current_user, mock_create_comment, mock_requests, client
):
    remove_decorators(client)
    mock_current_user_session(client, user_id=1)

    mock_current_user.return_value = type("User", (), {"id": 1})()
    mock_requests.get.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "post": {
                    "id": "123",
                    "title": "Test",
                    "content": "Contenido",
                    "created_at": "2025-09-21T00:00:00",
                    "updated_at": "2025-09-21T00:00:00",
                    "user_id": "1",
                    "username": "juan",
                }
            }
        ),
    )

    response = client.post(
        "/post/123/comment", data={"content": ""}, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Comentario vacío" in response.get_data(as_text=True)
    mock_create_comment.assert_not_called()


@patch("routes.comment_route.requests")
@patch("routes.comment_route.current_user")
def test_add_comment_post_not_found(mock_current_user, mock_requests, client):
    remove_decorators(client)
    mock_current_user_session(client, user_id=1)

    mock_current_user.return_value = type("User", (), {"id": 1})()
    mock_requests.get.return_value = Mock(
        status_code=404,
        json=Mock(return_value={"message": "Publicación no encontrada"}),
    )

    response = client.post("/post/123/comment", data={"content": "Hola"})
    assert response.status_code == 404


@patch("routes.comment_route.get_comment_or_404")
@patch("routes.comment_route.is_comment_owner_or_post_owner")
@patch("routes.comment_route.delete_comment_service")
@patch("routes.comment_route.current_user")
def test_delete_comment_success(
    mock_current_user, mock_delete, mock_is_owner, mock_get_comment, client
):
    remove_decorators(client)
    mock_current_user_session(client, user_id=1)

    mock_current_user.return_value = type("User", (), {"id": 1})()
    mock_is_owner.return_value = True
    mock_get_comment.return_value = type("Comment", (), {"id": 123, "post_id": 456})()

    response = client.post("/comment/123/delete", follow_redirects=True)
    assert response.status_code == 200
    assert "Comentario eliminado" in response.get_data(as_text=True)
    mock_delete.assert_called_once()


@patch("routes.comment_route.get_comment_or_404")
@patch("routes.comment_route.is_comment_owner_or_post_owner")
@patch("routes.comment_route.current_user")
def test_delete_comment_not_owner(
    mock_current_user, mock_is_owner, mock_get_comment, client
):
    remove_decorators(client)
    mock_current_user_session(client, user_id=1)

    mock_current_user.return_value = type("User", (), {"id": 1})()
    mock_is_owner.return_value = False
    mock_get_comment.return_value = type("Comment", (), {"id": 123, "post_id": 456})()

    response = client.post("/comment/123/delete")
    assert response.status_code == 403
