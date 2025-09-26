from unittest.mock import patch, MagicMock
from dtos import ApiRes


def test_get_posts_limit_success(client):
    mock_post = MagicMock()
    mock_post.to_json.return_value = {
        "id": "abc123",
        "title": "Título",
        "content": "Contenido",
        "created_at": "2025-09-21T14:00:00",
        "updated_at": "2025-09-21T14:00:00",
        "user_id": "1",
    }

    with patch(
        "db_connector.PostRepository.get_posts",
        return_value=ApiRes.success("OK", [mock_post]),
    ):
        response = client.get("/post/limit/1")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert len(response.json["data"]) == 1
        assert response.json["data"][0]["id"] == "abc123"


def test_get_posts_limit_error(client):
    with patch(
        "db_connector.PostRepository.get_posts",
        return_value=ApiRes.internal_error("Error al obtener las publicaciones"),
    ):
        response = client.get("/post/limit/1")
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error al obtener las publicaciones"


def test_get_posts_limit_success_no_title(client):
    mock_post = MagicMock()
    mock_post.to_json.return_value = {"id": "1", "title": "Hola", "content": "Texto"}

    with patch(
        "db_connector.PostRepository.get_posts",
        return_value=ApiRes.success("OK", [mock_post]),
    ):
        response = client.get("/post/limit/5")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert len(response.json["data"]) == 1


def test_get_posts_limit_success_with_title(client):
    mock_post = MagicMock()
    mock_post.to_json.return_value = {
        "id": "2",
        "title": "Hola mundo",
        "content": "Texto",
    }

    with patch(
        "db_connector.PostRepository.get_posts",
        return_value=ApiRes.success("OK", [mock_post]),
    ):
        response = client.get("/post/limit/5?title=Hola")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["data"][0]["title"].startswith("Hola")


def test_get_posts_limit_invalid_limit(client):
    response = client.get("/post/limit/0")
    assert response.status_code == 400
    assert response.json["message"] == "Limite < 1 no valido"
