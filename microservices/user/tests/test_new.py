from unittest.mock import patch, Mock
from routes import user_route
from datetime import datetime
from db_connector import User
from dtos import UserReqDto


def mock_user(id=1, username="juan", bio="Hola", created_at=datetime(2025, 1, 1)):
    user = Mock()
    user.id = id
    user.username = username
    user.bio = bio
    user.created_at = created_at
    user.to_json.return_value = {
        "id": id,
        "username": username,
        "bio": bio,
        "created_at": created_at.isoformat(),
    }

    return user


@patch("routes.user_route.exists_user")
@patch("routes.user_route.create_user")
def test_new_success(mock_create_user, mock_exists_user, client):
    mock_user_data = mock_user()
    mock_create_user.return_value = mock_user_data
    mock_exists_user.return_value = False

    response = client.post(
        "/u/new", json={"id": 1, "username": "juan"}, follow_redirects=True
    )

    assert response.status_code == 200
    assert response.json["success"]
    assert response.json["message"] == "Usuario creado"


@patch("routes.user_route.exists_user")
@patch("routes.user_route.create_user")
def test_new_exists(mock_create_user, mock_exists_user, client):
    mock_user_data = mock_user()
    mock_create_user.return_value = mock_user_data
    mock_exists_user.return_value = True

    response = client.post(
        "/u/new", json={"id": 1, "username": "juan"}, follow_redirects=True
    )

    assert response.status_code == 409
    assert response.json["success"] is False
    assert response.json["message"] == "El usuario ya existe"


def test_new_no_id(client):
    response = client.post("/u/new", json={"username": "juan"}, follow_redirects=True)

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Completa todos los campos"


def test_new_no_username(client):
    response = client.post("/u/new", json={"id": 1}, follow_redirects=True)

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Completa todos los campos"


@patch("routes.user_route.exists_user")
@patch("routes.user_route.create_user")
def test_error_new(mock_create_user, mock_exists_user, client):
    mock_create_user.return_value = None
    mock_exists_user.return_value = False

    response = client.post(
        "/u/new", json={"id": 1, "username": "juan"}, follow_redirects=True
    )

    assert response.status_code == 500
    assert response.json["success"] is False
    assert response.json["message"] == "Error al crear el usuario"
