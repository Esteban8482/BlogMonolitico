from unittest.mock import patch, Mock, MagicMock
from routes import post_route
from datetime import datetime
from db_connector import Post


def post_test(
    id=123,
    title="Nuevo post",
    content="Contenido",
    user_id=1,
    username="juan",
    created_at=datetime.now(),
    updated_at=datetime.now(),
):
    p = Post(
        id=id,
        title=title,
        content=content,
        user_id=user_id,
        username=username,
        created_at=created_at,
        updated_at=updated_at,
    )
    return p


def test_error_500_db(client):
    with patch("routes.post_route.get_post") as mock_get:
        mock_get.side_effect = Exception
        response = client.get("/post/123")
        assert response.status_code == 500


def test_post_detail_success(client):
    with patch("routes.post_route.get_post") as mock_post:
        mock_post.return_value = post_test()

        response = client.get("/post/123")

        print(response.json)

        assert response.status_code == 200
        assert response.json["success"] is True
        assert str(response.json["post"]["id"]) == "123"


def test_post_detail_not_found(client):
    with patch("routes.post_route.get_post", return_value=None):
        response = client.get("/post/999")
        assert response.status_code == 404
        assert response.json["success"] is False
        assert response.json["message"] == "Publicación no encontrada"
