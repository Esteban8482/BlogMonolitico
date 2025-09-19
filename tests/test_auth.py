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


@patch("routes.login_route.User.query")
def test_register_existing_user(mock_query, client):
    mock_query.filter.return_value.first.return_value = User()
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456",
        "confirm": "123456",
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert "Usuario o correo ya existe" in response.get_data(as_text=True)


@patch("routes.login_route.db.session")
@patch("routes.login_route.User.query")
def test_register_success(mock_query, mock_session, client):
    mock_query.filter.return_value.first.return_value = None
    data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "123456",
        "confirm": "123456",
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert "Registro exitoso" in response.get_data(as_text=True)


@patch("routes.login_route.User.query")
def test_login_invalid_credentials(mock_query, client):
    mock_query.filter.return_value.first.return_value = None
    data = {"username": "wrong", "password": "badpass"}
    response = client.post("/login", data=data)
    assert "Credenciales inválidas" in response.get_data(as_text=True)


@patch("routes.login_route.User.query")
def test_login_success(mock_query, client):
    user = User(id=1, username="test", email="test@example.com")
    user.check_password = lambda pwd: pwd == "123456"
    mock_query.filter.return_value.first.return_value = user
    data = {"username": "test", "password": "123456"}
    response = client.post("/login", data=data, follow_redirects=True)
    assert "Bienvenido de nuevo" in response.get_data(as_text=True)


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/logout", follow_redirects=True)
    assert "Sesión cerrada" in response.get_data(as_text=True)
