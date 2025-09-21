from unittest.mock import patch, Mock, MagicMock
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


def test_edit_post_get_success(client):
    mock_post = MagicMock()
    mock_post.to_json.return_value = {
        "id": "123",
        "title": "Título",
        "content": "Contenido",
    }
    mock_post.author.id = "1"

    with patch("routes.post_route.get_post", return_value=mock_post):
        response = client.get("/post/123/edit", headers={"X-User-ID": "1"})
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["post"]["id"] == "123"


def test_edit_post_no_auth_header(client):
    response = client.get("/post/123/edit")
    assert response.status_code == 403
    assert response.json["message"] == "No autorizado"


def test_edit_post_not_found(client):
    with patch("routes.post_route.get_post", return_value=None):
        response = client.get("/post/123/edit", headers={"X-User-ID": "1"})
        assert response.status_code == 404
        assert response.json["message"] == "Publicación no encontrada"


def test_edit_post_missing_fields(client):
    mock_post = MagicMock()
    mock_post.author.id = "1"

    with patch("routes.post_route.get_post", return_value=mock_post):
        response = client.post(
            "/post/123/edit",
            json={"title": "", "content": ""},
            headers={"X-User-ID": "1"},
        )
        assert response.status_code == 400
        assert response.json["message"] == "Campos requeridos"


def test_edit_post_success(client):
    mock_post = MagicMock()
    mock_post.author.id = "1"
    mock_updated = MagicMock()
    mock_updated.to_json.return_value = {
        "id": "123",
        "title": "Nuevo título",
        "content": "Nuevo contenido",
    }

    with patch("routes.post_route.get_post", return_value=mock_post):
        with patch("routes.post_route.update_post", return_value=mock_updated):
            response = client.post(
                "/post/123/edit",
                json={"title": "Nuevo título", "content": "Nuevo contenido"},
                headers={"X-User-ID": "1"},
            )
            assert response.status_code == 200
            assert response.json["success"] is True
