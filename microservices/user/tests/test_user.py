from unittest.mock import patch, Mock
from datetime import datetime
from db_connector import User
from dtos import ApiRes


def mock_user(id=1, username="juan", bio="Hola", created_at=datetime(2025, 1, 1)):
    return User(id=id, username=username, bio=bio, created_at=created_at)


@patch("db_connector.UserRepository.get_by_username")
def test_get_user_profile(mock_get_user, client):
    mock_get_user.return_value = ApiRes.success("Usuario encontrado", data=mock_user())

    response = client.get("/u/juan", headers={"X-User-ID": "1"})
    assert response.status_code == 200
    assert response.json["success"]
    assert response.json["message"] == "Perfil obtenido"
    assert response.json["data"]["username"] == "juan"


@patch("db_connector.UserRepository.get_by_username")
@patch("db_connector.UserRepository.save")
def test_update_user_bio_success(mock_save, mock_get_user, client):
    user = mock_user(bio="")
    updated_user = mock_user(bio="Hola")

    mock_get_user.return_value = ApiRes.success("Usuario encontrado", data=user)
    mock_save.return_value = ApiRes.success("Perfil actualizado", data=updated_user)

    response = client.post("/u/juan", headers={"X-User-ID": "1"}, json={"bio": "Hola"})

    assert response.status_code == 200
    assert response.json["success"]
    assert response.json["message"] == "Perfil actualizado"
    assert response.json["data"]["bio"] == "Hola"


@patch("db_connector.UserRepository.get_by_username")
def test_update_user_bio_not_owner(mock_get_user, client):
    mock_get_user.return_value = ApiRes.success(
        "Usuario encontrado", data=mock_user(id=2)
    )

    response = client.post(
        "/u/juan", headers={"X-User-ID": "1"}, json={"bio": "Nuevo bio"}
    )

    assert response.status_code == 403


def test_get_user_no_id(client):
    response = client.get("/u/juan")
    assert response.status_code == 401


@patch("db_connector.UserRepository.get_by_username")
def test_get_user_not_found(mock_get_user, client):
    mock_get_user.return_value = ApiRes.not_found("Usuario no encontrado")

    response = client.get("/u/juan", headers={"X-User-ID": "1"})
    assert response.status_code == 404


@patch("db_connector.UserRepository.get_by_username")
def test_update_user_bio_not_found(mock_get_user, client):
    mock_get_user.return_value = ApiRes.not_found("Usuario no encontrado")

    response = client.post("/u/juan", headers={"X-User-ID": "1"}, json={"bio": "Hola"})
    assert response.status_code == 404
