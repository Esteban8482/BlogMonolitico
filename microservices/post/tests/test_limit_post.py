from unittest.mock import patch, MagicMock


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

    with patch("routes.post_route.get_posts_service", return_value=[mock_post]):
        response = client.get("/post/limit/1")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert len(response.json["posts"]) == 1
        assert response.json["posts"][0]["id"] == "abc123"


def test_get_posts_limit_error(client):
    with patch(
        "routes.post_route.get_posts_service", side_effect=Exception("DB error")
    ):
        response = client.get("/post/limit/1")
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error al obtener las publicaciones"
