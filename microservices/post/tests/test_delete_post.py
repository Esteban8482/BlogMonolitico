from unittest.mock import patch, MagicMock
from dtos import ApiRes


def test_delete_post_success(client):
    mock_post = MagicMock()
    mock_post.user_id = "1"

    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.success("OK", mock_post),
    ):
        with patch(
            "db_connector.PostRepository.delete",
            return_value=ApiRes.success("Publicación eliminada"),
        ) as mock_delete:
            response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
            assert response.status_code == 200
            assert response.json["success"] is True
            assert response.json["message"] == "Publicación eliminada"
            mock_delete.assert_called_once_with("abc123")


def test_delete_post_no_auth_header(client):
    response = client.post("/post/abc123/delete")
    assert response.status_code == 401
    assert response.json["message"] == "No autorizado"


def test_delete_post_not_found(client):
    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.not_found("Publicación no encontrada"),
    ):
        response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
        assert response.status_code == 404
        assert response.json["message"] == "Publicación no encontrada"


def test_delete_post_wrong_author(client):
    mock_post = MagicMock()
    mock_post.user_id = "999"

    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.success("OK", mock_post),
    ):
        response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
        assert response.status_code == 403
        assert response.json["message"] == "Prohibido, no autorizado"


def test_delete_post_delete_error(client):
    mock_post = MagicMock()
    mock_post.user_id = "1"

    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.success("OK", mock_post),
    ):
        with patch(
            "db_connector.PostRepository.delete",
            return_value=ApiRes.internal_error("Error al eliminar la publicación"),
        ):
            response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
            assert response.status_code == 500
            assert response.json["message"] == "Error al eliminar la publicación"
