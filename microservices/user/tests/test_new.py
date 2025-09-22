from unittest.mock import patch, Mock
from datetime import datetime

from db_connector import User
from dtos import ApiRes
from routes import user_api  # Asegúrate que esté registrado en Flask app


def mock_user(id=1, username="juan", bio="Hola", created_at=datetime(2025, 1, 1)):
    return User(id=id, username=username, bio=bio, created_at=created_at)


@patch("db_connector.UserRepository.exists_by_username_or_id")
@patch("db_connector.UserRepository.save")
def test_new_success(mock_save, mock_exists, client):
    mock_exists.return_value = ApiRes.not_found("Usuario no encontrado", data=False)
    mock_save.return_value = ApiRes.created(
        "Usuario guardado correctamente", data=mock_user()
    )

    response = client.post("/u/new", json={"id": 1, "username": "juan"})

    assert response.status_code == 200
    assert response.json["success"]
    assert response.json["message"] == "Usuario creado"


@patch("db_connector.UserRepository.exists_by_username_or_id")
def test_new_exists(mock_exists, client):
    mock_exists.return_value = ApiRes.success("Usuario encontrado", data=True)

    response = client.post("/u/new", json={"id": 1, "username": "juan"})

    assert response.status_code == 409
    assert response.json["success"] is False
    assert response.json["message"] == "El usuario ya existe"


def test_new_no_id(client):
    response = client.post("/u/new", json={"username": "juan"})

    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Completa todos los campos" in response.json["message"]


def test_new_no_username(client):
    response = client.post("/u/new", json={"id": 1})

    assert response.status_code == 400
    assert response.json["success"] is False
    assert "Completa todos los campos" in response.json["message"]


@patch("db_connector.UserRepository.exists_by_username_or_id")
@patch("db_connector.UserRepository.save")
def test_error_new(mock_save, mock_exists, client):
    mock_exists.return_value = ApiRes.not_found("Usuario no encontrado", data=False)
    mock_save.return_value = ApiRes.internal_error("Error al guardar el usuario")

    response = client.post("/u/new", json={"id": 1, "username": "juan"})

    assert response.status_code == 500
    assert response.json["success"] is False
    assert response.json["message"] == "Error al guardar el usuario"
