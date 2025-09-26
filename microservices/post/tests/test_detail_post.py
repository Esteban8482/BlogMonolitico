from unittest.mock import patch
from datetime import datetime
from db_connector import Post
from dtos import ApiRes


# Utilidad para crear un post simulado
def post_test(
    id=123,
    title="Nuevo post",
    content="Contenido",
    user_id=1,
    username="juan",
    created_at=datetime.now(),
    updated_at=datetime.now(),
):
    return Post(
        id=id,
        title=title,
        content=content,
        user_id=user_id,
        username=username,
        created_at=created_at,
        updated_at=updated_at,
    )


def test_post_detail_success(client):
    mock_post = post_test()
    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.success("OK", mock_post),
    ):
        response = client.get("/post/123")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert str(response.json["data"]["id"]) == "123"


def test_error_500_db(client):
    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.internal_error("Error interno simulado"),
    ):
        response = client.get("/post/123")
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error interno simulado"


def test_post_detail_not_found(client):
    with patch(
        "db_connector.PostRepository.get_by_id",
        return_value=ApiRes.not_found("Publicación no encontrada"),
    ):
        response = client.get("/post/999")
        assert response.status_code == 404
        assert response.json["success"] is False
        assert response.json["message"] == "Publicación no encontrada"
