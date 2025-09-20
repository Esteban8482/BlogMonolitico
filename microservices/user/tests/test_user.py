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


@patch("routes.user_route.get_user_or_404")
def test_get_user_profile(mock_get_user, client):
    mock_user_data = mock_user()
    mock_get_user.return_value = mock_user_data

    response = client.get("/u/juan", headers={"X-User-ID": 1})
    assert response.status_code == 200
    assert "Hola" in response.get_data(as_text=True)

    user = UserReqDto.from_json(response.json["profile_user"])

    assert user.id == 1
    assert user.username == "juan"


@patch("routes.user_route.update_user_bio")
@patch("routes.user_route.get_user_or_404")
def test_update_user_bio_success(mock_get_user, mock_update, client):
    mock_user_data = mock_user(bio="")
    mock_user_data_updated = mock_user(bio="Hola")

    mock_get_user.return_value = mock_user_data
    mock_update.return_value = mock_user_data_updated

    response = client.post(
        "/u/juan", headers={"X-User-ID": 1}, json={"bio": "Hola"}, follow_redirects=True
    )

    assert response.status_code == 200
    assert response.json["success"]
    assert response.json["message"] == "Perfil actualizado"

    user = User.from_json(response.json["profile_user"])
    assert user.id == 1
    assert user.username == "juan"
    assert user.bio == "Hola"


@patch("routes.user_route.update_user_bio")
@patch("routes.user_route.get_user_or_404")
def test_update_user_bio_not_owner(mock_get_user, mock_update, client):
    mock_user_owner = mock_user(id=2)
    mock_get_user.return_value = mock_user_owner

    response = client.post(
        "/u/juan",
        headers={"X-User-ID": 1},
        json={"bio": "Nuevo bio"},
        follow_redirects=True,
    )

    assert response.status_code == 403
    mock_update.assert_not_called()


def test_get_user_no_id(client):
    response = client.get("/u/juan")
    assert response.status_code == 403


@patch("routes.user_route.get_user_or_404")
def test_get_user_no_username(mock_get_user, client):
    mock_user_data = mock_user()
    mock_get_user.return_value = mock_user_data

    response = client.get("/u/", headers={"X-User-ID": 1})
    assert response.status_code == 404


def test_update_user_no_id(client):
    response = client.post(
        "/u/juan", headers={"X-User-ID": 1}, json={"bio": "Hola"}, follow_redirects=True
    )
    assert response.status_code == 404


@patch("routes.user_route.get_user_or_404")
def test_update_user_no_username(mock_get_user, client):
    mock_user_data = mock_user()
    mock_get_user.return_value = mock_user_data

    response = client.post(
        "/u/", headers={"X-User-ID": 1}, json={"bio": "Hola"}, follow_redirects=True
    )
    assert response.status_code == 404
