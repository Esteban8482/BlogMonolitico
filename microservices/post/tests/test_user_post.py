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
