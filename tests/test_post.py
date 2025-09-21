from unittest.mock import patch, Mock
from routes import post_route
from datetime import datetime


def mock_current_user(client, user_id=1):
    # Simula usuario autenticado
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    # Reemplaza la vista decorada por la versión original sin decorador
    client.application.view_functions[
        "post.create_post"
    ] = post_route.create_post.__wrapped__
    client.application.view_functions[
        "post.edit_post"
    ] = post_route.edit_post.__wrapped__
    client.application.view_functions[
        "post.delete_post"
    ] = post_route.delete_post.__wrapped__
    client.application.view_functions[
        "post.post_detail"
    ] = post_route.post_detail.__wrapped__


@patch("routes.post_route.requests")
@patch("routes.post_route.current_user")
def test_create_post_success(mock_current_user_func, mock_requests, client):
    mock_current_user_func.return_value = type(
        "User", (), {"id": 1, "username": "juan"}
    )()
    mock_requests.post.return_value = Mock(
        status_code=201,
        json=Mock(
            return_value={
                "message": "Publicación creada",
                "post": {
                    "id": "p1",
                    "title": "Nuevo post",
                    "content": "Contenido",
                    "created_at": "2025-09-21",
                    "updated_at": "2025-09-21",
                    "user_id": "1",
                    "username": "juan",
                },
            }
        ),
    )

    response = client.post(
        "/post/new", data={"title": "Nuevo post", "content": "Contenido"}
    )
    assert response.status_code == 302


@patch("routes.post_route.requests")
@patch("routes.post_route.current_user")
def test_edit_post_success(mock_current_user_func, mock_requests, client):
    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_requests.post.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "message": "Publicación actualizada",
                "post": {
                    "id": "p1",
                    "title": "Editado",
                    "content": "Nuevo contenido",
                    "created_at": "2025-09-21",
                    "updated_at": "2025-09-21",
                    "user_id": "1",
                    "username": "juan",
                },
            }
        ),
    )

    response = client.post(
        "/post/1/edit", data={"title": "Editado", "content": "Nuevo contenido"}
    )
    assert response.status_code == 302


@patch("routes.post_route.requests")
@patch("routes.post_route.current_user")
def test_delete_post_success(mock_current_user_func, mock_requests, client):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_requests.post.return_value = Mock(
        status_code=200, json=Mock(return_value={"message": "Publicación eliminada"})
    )

    response = client.post("/post/1/delete")
    assert response.status_code == 302


@patch("routes.post_route.requests")
@patch("routes.post_route.current_user")
@patch("routes.post_route.get_post_comments")
def test_post_detail_success(
    mock_comments, mock_current_user_func, mock_requests, client
):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_requests.get.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "post": {
                    "id": "p1",
                    "title": "Post 1",
                    "content": "Contenido",
                    "created_at": "2025-09-21",
                    "updated_at": "2025-09-21",
                    "user_id": "1",
                    "username": "juan",
                }
            }
        ),
    )
    mock_comments.return_value = []

    response = client.get("/post/p1")
    assert response.status_code == 200
    assert "Post 1" in response.get_data(as_text=True)
