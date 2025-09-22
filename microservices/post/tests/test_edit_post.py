from unittest.mock import patch, MagicMock
from datetime import datetime
from db_connector import Post
from dtos import ApiRes


# Utilidad para crear un post simulado
def mock_post(
    id="123",
    title="Nuevo post",
    content="Contenido",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    user_id="1",
    username="juan",
):
    post = MagicMock()
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


def test_edit_post_success(client):
    post = mock_post()  # Este es el objeto que se modificará
    update_post = mock_post(title="Update")

    with (
        patch(
            "db_connector.PostRepository.get_by_id",
            return_value=ApiRes.success("OK", post),
        ),
        patch(
            "db_connector.PostRepository.save",
            return_value=ApiRes.success("OK", update_post),
        ),
    ):
        response = client.post(
            "/post/123/edit",
            json={"title": "Nuevo título", "content": "Nuevo contenido"},
            headers={"X-User-ID": "1"},
        )
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["data"]["title"] == "Update"


def test_edit_post_no_auth_header(client):
    response = client.get("/post/123/edit")
    assert response.status_code == 401
    assert response.json["message"] == "No autorizado"


def test_edit_post_not_found(client):
    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.not_found("Publicación no encontrada"),
    ):
        response = client.get("/post/123/edit", headers={"X-User-ID": "1"})
        assert response.status_code == 404
        assert response.json["message"] == "Publicación no encontrada"


def test_edit_post_missing_fields(client):
    post = mock_post()
    with patch(
        "db_connector.PostRepository.get_by_id", return_value=ApiRes.success("OK", post)
    ):
        response = client.post(
            "/post/123/edit",
            json={"title": "", "content": ""},
            headers={"X-User-ID": "1"},
        )
        assert response.status_code == 400
        assert response.json["message"] == "Título y contenido requeridos"


def test_edit_post_success(client):
    post = mock_post()
    updated_post = mock_post(title="Nuevo título", content="Nuevo contenido")
    with (
        patch(
            "db_connector.PostRepository.get_by_id",
            return_value=ApiRes.success("OK", post),
        ),
        patch(
            "db_connector.PostRepository.save",
            return_value=ApiRes.success("Actualizado", updated_post),
        ),
    ):
        response = client.post(
            "/post/123/edit",
            json={"title": "Nuevo título", "content": "Nuevo contenido"},
            headers={"X-User-ID": "1"},
        )
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["data"]["title"] == "Nuevo título"
