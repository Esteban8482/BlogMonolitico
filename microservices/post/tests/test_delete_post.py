from unittest.mock import patch, MagicMock


def test_delete_post_success(client):
    mock_post = MagicMock()
    mock_post.author.id = "1"

    with patch("routes.post_route.get_post", return_value=mock_post):
        with patch("routes.post_route.delete_post_service") as mock_delete:
            response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
            assert response.status_code == 200
            assert response.json["success"] is True
            assert response.json["message"] == "Publicación eliminada"
            mock_delete.assert_called_once_with(mock_post)


def test_delete_post_no_auth_header(client):
    response = client.post("/post/abc123/delete")
    assert response.status_code == 403
    assert response.json["message"] == "No autorizado"


def test_delete_post_not_found(client):
    with patch("routes.post_route.get_post", return_value=None):
        response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
        assert response.status_code == 404
        assert response.json["message"] == "Publicación no encontrada"


def test_delete_post_wrong_author(client):
    mock_post = MagicMock()
    mock_post.author.id = "999"  # distinto al user_id

    with patch("routes.post_route.get_post", return_value=mock_post):
        response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
        assert response.status_code == 403
        assert response.json["message"] == "No autorizado"


def test_delete_post_delete_error(client):
    mock_post = MagicMock()
    mock_post.author.id = "1"

    with patch("routes.post_route.get_post", return_value=mock_post):
        with patch(
            "routes.post_route.delete_post_service",
            side_effect=Exception("Delete failed"),
        ):
            response = client.post("/post/abc123/delete", headers={"X-User-ID": "1"})
            assert response.status_code == 500
            assert response.json["message"] == "Error al eliminar la publicación"
