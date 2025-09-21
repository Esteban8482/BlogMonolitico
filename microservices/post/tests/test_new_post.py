from unittest.mock import patch, Mock
from routes import post_route
from datetime import datetime
from db_connector import Post


def mock_post(
    id=123,
    title="Nuevo post",
    content="Contenido",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    user_id=1,
    username="juan",
):
    post = Mock()
    post.id = id
    post.title = title
    post.content = content
    post.created_at = created_at
    post.updated_at = updated_at
    post.user_id = user_id
    post.username = username
    post.to_json.return_value = {
        "id": id,
        "title": title,
        "content": content,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "user_id": user_id,
        "username": username,
    }
    return post


def test_create_post_success(client):
    data = {"title": "Nuevo post", "content": "Contenido"}

    # Mockea funciones internas
    with (patch("routes.post_route.create_post_service") as mock_create,):
        mock_create.return_value = mock_post()
        response = client.post("/post/new", json=data, headers={"X-User-ID": 1})
        assert response.status_code == 201


def test_create_post_missing_fields(client):
    data = {"title": "", "content": ""}
    response = client.post("/post/new", json=data, headers={"X-User-ID": 1})

    assert response.status_code == 400


def test_create_post_no_json(client):
    data = {"title": "", "content": ""}
    response = client.post("/post/new", data=data)

    assert response.status_code == 403


def test_create_post_no_user_id(client):
    data = {"title": "Nuevo post", "content": "Contenido"}
    response = client.post("/post/new", json=data)

    assert response.status_code == 403


def test_error_500_db(client):
    with patch("routes.post_route.create_post_service") as mock_create:
        mock_create.side_effect = Exception

        response = client.post(
            "/post/new",
            json={"title": "Nuevo post", "content": "Contenido"},
            headers={"X-User-ID": 1},
        )

        assert response.status_code == 500
