from unittest.mock import patch, MagicMock
from dtos import ApiRes


def test_user_posts_success(client):
    mock_post = MagicMock()
    mock_post.to_json.return_value = {
        "id": "abc123",
        "title": "Título",
        "content": "Contenido",
        "created_at": "2025-09-21T14:00:00",
        "updated_at": "2025-09-21T14:00:00",
        "user_id": "1",
        "username": "juan",
    }

    with patch(
        "db_connector.PostRepository.get_user_posts",
        return_value=ApiRes.success("OK", [mock_post]),
    ):
        response = client.get("/post/user/1")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert isinstance(response.json["data"], list)
        assert response.json["data"][0]["id"] == "abc123"


def test_user_posts_not_found(client):
    with patch(
        "db_connector.PostRepository.get_user_posts",
        return_value=ApiRes.not_found("No hay publicaciones"),
    ):
        response = client.get("/post/user/999")
        assert response.status_code == 404
        assert response.json["success"] is False
        assert response.json["message"] == "No hay publicaciones"


def test_user_posts_error(client):
    with patch(
        "db_connector.PostRepository.get_user_posts",
        return_value=ApiRes.internal_error("Error al obtener publicaciones"),
    ):
        response = client.get("/post/user/1")
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error al obtener publicaciones"
