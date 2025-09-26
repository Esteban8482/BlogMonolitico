from unittest.mock import patch
from dtos import ApiRes


def test_exists_post_true(client):
    with patch(
        "db_connector.PostRepository.exists",
        return_value=ApiRes.success("Existe", data=True),
    ):
        response = client.get("/post/abc123/exists")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["data"] is True


def test_exists_post_false(client):
    with patch(
        "db_connector.PostRepository.exists",
        return_value=ApiRes.not_found("Publicación no encontrada"),
    ):
        response = client.get("/post/abc123/exists")
        assert response.status_code == 404
        assert response.json["success"] is False
        assert response.json["message"] == "Publicación no encontrada"


def test_exists_post_error(client):
    with patch(
        "db_connector.PostRepository.exists",
        return_value=ApiRes.internal_error("Error al verificar la publicación"),
    ):
        response = client.get("/post/abc123/exists")
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error al verificar la publicación"
