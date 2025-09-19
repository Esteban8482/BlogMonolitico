from unittest.mock import patch
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
        "post.delete_post_view"
    ] = post_route.delete_post_view.__wrapped__


def test_create_post_success(client):
    remove_decorators(client)
    mock_current_user(client)
    data = {"title": "Nuevo post", "content": "Contenido"}

    # Mockea funciones internas
    with (
        patch("routes.post_route.current_user") as mock_user,
        patch("routes.post_route.create_post") as mock_create,
    ):
        mock_user.return_value = type("User", (), {"id": 1})()
        mock_create.return_value = type("Post", (), {"id": 123})()

        response = client.post("/post/new", data=data, follow_redirects=True)

        assert "Publicación creada" in response.get_data(as_text=True)
        mock_create.assert_called_once_with("Nuevo post", "Contenido", 1)


def test_create_post_missing_fields(client):
    remove_decorators(client)
    mock_current_user(client)
    data = {"title": "", "content": ""}

    response = client.post("/post/new", data=data, follow_redirects=True)

    assert "Título y contenido requeridos" in response.get_data(as_text=True)


def test_edit_post_success(client):
    remove_decorators(client)
    mock_current_user(client)
    data = {"title": "Editado", "content": "Nuevo contenido"}

    with (
        patch("routes.post_route.current_user") as mock_user,
        patch("routes.post_route.get_post_or_404") as mock_get,
        patch("routes.post_route.update_post") as mock_update,
    ):
        mock_user.return_value = type("User", (), {"id": 1})()
        mock_get.return_value = type(
            "Post",
            (),
            {
                "id": 123,
                "author": mock_user.return_value,
                "created_at": datetime(2025, 9, 19, 14, 30),
            },
        )()
        mock_update.return_value = None

        response = client.post("/post/123/edit", data=data, follow_redirects=True)

        assert "Publicación actualizada" in response.get_data(as_text=True)
        mock_update.assert_called_once_with(
            mock_get.return_value, "Editado", "Nuevo contenido"
        )


def test_edit_post_missing_fields(client):
    remove_decorators(client)
    mock_current_user(client)
    data = {"title": "", "content": ""}

    with (
        patch("routes.post_route.current_user") as mock_user,
        patch("routes.post_route.get_post_or_404") as mock_get,
    ):
        mock_user.return_value = type("User", (), {"id": 1})()
        mock_get.return_value = type(
            "Post",
            (),
            {
                "id": 123,
                "author": mock_user.return_value,
                "created_at": datetime(2025, 9, 19, 14, 30),
            },
        )()

        response = client.post("/post/123/edit", data=data, follow_redirects=True)

        assert "Campos requeridos" in response.get_data(as_text=True)


def test_edit_post_not_owner(client):
    remove_decorators(client)
    # Simula usuario autenticado con ID 2
    mock_current_user(client, user_id=2)

    data = {"title": "Editado", "content": "Nuevo contenido"}

    with (
        patch("routes.post_route.current_user") as mock_user,
        patch("routes.post_route.get_post_or_404") as mock_get,
    ):
        # Usuario actual es ID 2
        mock_user.return_value = type("User", (), {"id": 2})()

        # El autor del post es ID 1
        mock_get.return_value = type(
            "Post",
            (),
            {
                "id": 123,
                "author": type("User", (), {"id": 1})(),
                "created_at": datetime(2025, 9, 19, 14, 30),
                "title": "Título original",
                "content": "Contenido original",
            },
        )()

        response = client.post("/post/123/edit", data=data, follow_redirects=True)

        assert response.status_code == 403


def test_delete_post_success(client):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    with (
        patch("routes.post_route.current_user") as mock_user,
        patch("routes.post_route.get_post_or_404") as mock_get,
        patch("routes.post_route.delete_post") as mock_delete,
    ):
        # Usuario actual es ID 1
        mock_user.return_value = type("User", (), {"id": 1})()
        mock_delete.return_value = None

        # El autor del post es ID 1
        mock_get.return_value = type(
            "Post",
            (),
            {
                "id": 123,
                "author": type("User", (), {"id": 1})(),
                "created_at": datetime(2025, 9, 19, 14, 30),
            },
        )()

        response = client.post("/post/123/delete", follow_redirects=True)

        assert "Publicación eliminada" in response.get_data(as_text=True)
        mock_delete.assert_called_once_with(mock_get.return_value)


def test_delete_post_not_owner(client):
    remove_decorators(client)
    mock_current_user(client, user_id=2)

    with (
        patch("routes.post_route.current_user") as mock_user,
        patch("routes.post_route.get_post_or_404") as mock_get,
        patch("routes.post_route.delete_post") as mock_delete,
    ):
        # Usuario actual es ID 2
        mock_user.return_value = type("User", (), {"id": 2})()

        # El autor del post es ID 1
        mock_get.return_value = type(
            "Post",
            (),
            {
                "id": 123,
                "author": type("User", (), {"id": 1})(),
                "created_at": datetime(2025, 9, 19, 14, 30),
            },
        )()

        response = client.post("/post/123/delete", follow_redirects=True)

        assert response.status_code == 403
