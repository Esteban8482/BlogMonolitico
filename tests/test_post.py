from unittest.mock import patch
from routes import post_route
from datetime import datetime
from dtos import PostDto


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


@patch("routes.post_route.create_post_service")
@patch("routes.post_route.current_user")
def test_create_post_success(mock_current_user_func, mock_create_post, client):
    mock_current_user_func.return_value = type(
        "User", (), {"id": 1, "username": "juan"}
    )()

    mock_create_post.return_value = PostDto(
        id="p1",
        title="Nuevo post",
        content="Contenido",
        created_at=datetime(2025, 9, 21),
        updated_at=datetime(2025, 9, 21),
        user_id="1",
        username="juan",
    )

    response = client.post(
        "/post/new", data={"title": "Nuevo post", "content": "Contenido"}
    )
    assert response.status_code == 302


@patch("routes.post_route.update_post")
@patch("routes.post_route.current_user")
def test_edit_post_success(mock_current_user_func, mock_update_post, client):
    mock_current_user_func.return_value = type("User", (), {"id": 1})()

    mock_update_post.return_value = PostDto(
        id="p1",
        title="Editado",
        content="Nuevo contenido",
        created_at=datetime(2025, 9, 21),
        updated_at=datetime(2025, 9, 21),
        user_id="1",
        username="juan",
    )

    response = client.post(
        "/post/p1/edit", data={"title": "Editado", "content": "Nuevo contenido"}
    )
    assert response.status_code == 302


@patch("routes.post_route.delete_post_by_id")
@patch("routes.post_route.current_user")
def test_delete_post_success(mock_current_user_func, mock_delete_post, client):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_delete_post.return_value = True

    response = client.post("/post/p1/delete")
    assert response.status_code == 302


@patch("routes.post_route.get_post")
@patch("routes.post_route.get_post_comments")
@patch("routes.post_route.current_user")
def test_post_detail_success(
    mock_current_user_func, mock_comments, mock_get_post, client
):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_get_post.return_value = PostDto(
        id="p1",
        title="Post 1",
        content="Contenido",
        created_at=datetime(2025, 9, 21),
        updated_at=datetime(2025, 9, 21),
        user_id="1",
        username="juan",
    )
    mock_comments.return_value = []

    response = client.get("/post/p1")
    assert response.status_code == 200
    assert "Post 1" in response.get_data(as_text=True)


@patch("routes.post_route.create_post_service")
@patch("routes.post_route.current_user")
def test_create_post_failure(mock_current_user_func, mock_create_post, client):
    mock_current_user_func.return_value = type(
        "User", (), {"id": 1, "username": "juan"}
    )()
    mock_create_post.return_value = None  # Simula fallo

    response = client.post("/post/new", data={"title": "Fallido", "content": "Error"})
    assert response.status_code == 302
    assert "/post/new" in response.headers["Location"]


@patch("routes.post_route.update_post")
@patch("routes.post_route.current_user")
def test_edit_post_failure(mock_current_user_func, mock_update_post, client):
    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_update_post.return_value = None  # Simula fallo

    response = client.post(
        "/post/p1/edit", data={"title": "Error", "content": "Fallido"}
    )
    assert response.status_code == 302
    assert "/post/p1/edit" in response.headers["Location"]


@patch("routes.post_route.get_post")
@patch("routes.post_route.current_user")
def test_post_detail_failure(mock_current_user_func, mock_get_post, client):
    remove_decorators(client)
    mock_current_user(client, user_id=1)

    mock_current_user_func.return_value = type("User", (), {"id": 1})()
    mock_get_post.return_value = None  # Simula fallo

    response = client.get("/post/p1")
    assert response.status_code == 400
