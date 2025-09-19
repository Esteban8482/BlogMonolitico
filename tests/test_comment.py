from unittest.mock import patch
from routes import comment_route
from datetime import datetime


def mock_current_user(client, user_id=1):
    # Simula usuario autenticado
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def remove_decorators(client):
    # Reemplaza la vista decorada por la versión original sin decorador
    client.application.view_functions[
        "comment.add_comment"
    ] = comment_route.add_comment.__wrapped__
    client.application.view_functions[
        "comment.delete_comment_view"
    ] = comment_route.delete_comment_view.__wrapped__


@patch("routes.comment_route.create_comment")
@patch("routes.comment_route.current_user")
@patch("routes.comment_route.get_post_or_404")
def test_add_comment_success(mock_user, mock_create, mock_get, client):
    remove_decorators(client)
    mock_current_user(client)

    mock_user.return_value = type("User", (), {"id": 1})()
    mock_create.return_value = type("Comment", (), {"id": 456})()
    mock_get.return_value = type("Post", (), {"id": 123})()

    response = client.post(
        "/post/123/comment", data={"content": "Hola"}, follow_redirects=True
    )
    assert "Comentario agregado" in response.get_data(as_text=True)


@patch("routes.comment_route.create_comment")
@patch("routes.comment_route.current_user")
@patch("routes.comment_route.get_post_or_404")
def test_add_comment_not_owner(mock_user, mock_create, mock_get, client):
    remove_decorators(client)
    mock_current_user(client, user_id=2)
    mock_user.return_value = type("User", (), {"id": 2})()
    mock_create.return_value = type("Comment", (), {"id": 456})()
    mock_get.return_value = type("Post", (), {"id": 123})()

    response = client.post(
        "/post/123/comment", data={"content": "Hola"}, follow_redirects=True
    )

    assert "Comentario agregado" in response.get_data(as_text=True)


@patch("routes.comment_route.create_comment")
@patch("routes.comment_route.current_user")
@patch("routes.comment_route.get_post_or_404")
def test_add_comment_missing_fields(mock_user, mock_create, mock_get, client):
    remove_decorators(client)
    mock_current_user(client)

    mock_user.return_value = type("User", (), {"id": 1})()
    mock_create.return_value = type("Comment", (), {"id": 456})()
    mock_get.return_value = type("Post", (), {"id": 123})()

    response = client.post(
        "/post/123/comment", data={"content": ""}, follow_redirects=True
    )

    assert "Comentario vacío" in response.get_data(as_text=True)


@patch("routes.comment_route.create_comment")
@patch("routes.comment_route.current_user")
@patch("routes.comment_route.get_post_or_404")
def test_add_comment_no_login(mock_user, mock_create, mock_get, client):
    mock_user.return_value = None
    mock_create.return_value = type("Comment", (), {"id": 456})()
    mock_get.return_value = type("Post", (), {"id": 123})()

    response = client.post(
        "/post/123/comment", data={"content": "Hola"}, follow_redirects=True
    )
    assert "Debes iniciar sesión." in response.get_data(as_text=True)


@patch("routes.comment_route.is_comment_owner_or_post_owner")
@patch("routes.comment_route.delete_comment")
@patch("routes.comment_route.get_comment_or_404")
@patch("routes.comment_route.current_user")
def test_delete_comment_success(
    mock_user, mock_get, mock_delete, mock_is_owner, client
):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_user.return_value = type("User", (), {"id": 1})()
    mock_is_owner.return_value = True
    mock_delete.return_value = None

    post = type("Post", (), {"id": 456, "author": mock_user.return_value})()

    # Simula comentario
    mock_get.return_value = type(
        "Comment",
        (),
        {
            "id": 123,
            "post": post,
            "author": mock_user.return_value,
        },
    )

    response = client.post("/comment/123/delete", follow_redirects=True)
    assert "Comentario eliminado" in response.get_data(as_text=True)
    mock_delete.assert_called_once_with(mock_get.return_value)


@patch("routes.comment_route.is_comment_owner_or_post_owner")
@patch("routes.comment_route.delete_comment")
@patch("routes.comment_route.get_comment_or_404")
@patch("routes.comment_route.current_user")
def test_delete_comment_not_owner(
    mock_user, mock_get, mock_delete, mock_is_owner, client
):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_user.return_value = type("User", (), {"id": 2})()
    mock_is_owner.return_value = False
    mock_delete.return_value = None

    post = type("Post", (), {"id": 456, "author": mock_user.return_value})()

    # Simula comentario
    mock_get.return_value = type(
        "Comment",
        (),
        {
            "id": 123,
            "post": post,
            "author": mock_user.return_value,
        },
    )

    response = client.post("/comment/123/delete", follow_redirects=True)

    assert response.status_code == 403
