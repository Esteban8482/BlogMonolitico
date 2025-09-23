from unittest.mock import patch
from dtos import ApiRes
from datetime import datetime
from db_connector import Post


def mock_post(
    id="123",
    title="Nuevo post",
    content="Contenido",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    user_id="1",
    username="juan",
):
    post = Post(
        id=id,
        title=title,
        content=content,
        created_at=created_at,
        updated_at=updated_at,
        user_id=user_id,
        username=username,
    )
    return post


def test_create_post_success(client):
    post = mock_post()
    with patch(
        "db_connector.PostRepository.save", return_value=ApiRes.created("Creado", post)
    ):
        response = client.post(
            "/post/new",
            json={
                "title": post.title,
                "content": post.content,
                "username": post.username,
            },
            headers={"X-User-ID": post.user_id},
        )
        assert response.status_code == 201
        assert response.json["success"] is True
        assert response.json["data"]["title"] == "Nuevo post"


def test_create_post_missing_fields(client):
    response = client.post(
        "/post/new", json={"title": "", "content": ""}, headers={"X-User-ID": "1"}
    )
    assert response.status_code == 400
    assert response.json["message"] == "Título y contenido requeridos"


def test_create_post_no_json(client):
    response = client.post("/post/new", data={"title": "", "content": ""})
    assert response.status_code == 401
    assert response.json["message"] == "No autorizado"


# Sin cabecera de usuario
def test_create_post_no_user_id(client):
    response = client.post(
        "/post/new", json={"title": "Nuevo post", "content": "Contenido"}
    )
    assert response.status_code == 401
    assert response.json["message"] == "No autorizado"


# Error interno al guardar
def test_error_500_db(client):
    with patch(
        "db_connector.PostRepository.save",
        return_value=ApiRes.internal_error("Error al guardar"),
    ):
        response = client.post(
            "/post/new",
            json={"title": "Nuevo post", "content": "Contenido", "username": "juan"},
            headers={"X-User-ID": "1"},
        )
        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["message"] == "Error al guardar"
