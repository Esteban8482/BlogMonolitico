from unittest.mock import patch
from db_connector import User


def test_register_missing_fields(client):
    response = client.post("/register", data={})
    assert b"Completa todos los campos" in response.data


def test_register_password_mismatch(client):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456",
        "confirm": "654321",
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert "Las contraseñas no coinciden" in response.get_data(as_text=True)


@patch("routes.login_route.register_user")
def test_register_existing_user(mock_register, client):
    mock_register.return_value = None
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456",
        "confirm": "123456",
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert "Usuario o correo ya existe" in response.get_data(as_text=True)


@patch("routes.login_route.register_user")
@patch("routes.login_route.requests")
def test_register_success(mock_req, mock_register_user, client):
    user = type("User", (), {"id": 1})()
    mock_register_user.return_value = user
    # requests al microservicio de usuario
    mock_req.post.return_value.status_code = 200

    data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "123456",
        "confirm": "123456",
    }

    response = client.post("/register", data=data, follow_redirects=True)

    assert "Registro exitoso" in response.get_data(as_text=True)
    mock_register_user.assert_called_once_with("newuser", "new@example.com", "123456")


@patch("routes.login_route.register_user")
def test_register_user_exists(mock_register_user, client):
    mock_register_user.return_value = None  # Simula fallo por usuario duplicado

    data = {
        "username": "existing",
        "email": "existing@example.com",
        "password": "123456",
        "confirm": "123456",
    }

    response = client.post("/register", data=data, follow_redirects=True)
    assert "Usuario o correo ya existe" in response.get_data(as_text=True)


@patch("routes.login_route.authenticate_user")
def test_login_invalid_credentials(mock_authenticate_user, client):
    mock_authenticate_user.return_value = None
    data = {"username": "wrong", "password": "badpass"}
    response = client.post("/login", data=data)
    assert "Credenciales inválidas" in response.get_data(as_text=True)


@patch("routes.login_route.authenticate_user")
def test_login_success(mock_authenticate_user, client):
    # Simula usuario autenticado
    user = type("User", (), {"id": 1})()
    mock_authenticate_user.return_value = user

    # Mock de la vista index
    client.application.view_functions["index"] = lambda: "Página de inicio simulada"

    data = {"username": "test", "password": "123456"}
    response = client.post("/login", data=data, follow_redirects=True)

    assert "Página de inicio simulada" in response.get_data(as_text=True)
    mock_authenticate_user.assert_called_once_with("test", "123456")


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    # Mock de la vista index
    client.application.view_functions["index"] = lambda: "Página de inicio simulada"
    response = client.get("/logout", follow_redirects=True)

    assert "Página de inicio simulada" in response.get_data(as_text=True)
