from unittest.mock import patch, MagicMock


def test_exists_post_true(client):
    with patch("routes.post_route.exists_post_service", return_value=True):
        response = client.get("/post/abc123/exists")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["exists"] is True


def test_exists_post_false(client):
    with patch("routes.post_route.exists_post_service", return_value=False):
        response = client.get("/post/abc123/exists")
        assert response.status_code == 404
        assert response.json["success"] is False
        assert response.json["message"] == "Publicación no encontrada"


def test_exists_post_error(client):
    with patch(
        "routes.post_route.exists_post_service", side_effect=Exception("DB error")
    ):
        response = client.get("/post/abc123/exists")
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error al verificar la publicación"
