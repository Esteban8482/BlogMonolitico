from db_connector import User


def mock_current_user(user_id=1):
    return User(id=user_id, username="testuser", email="test@example.com")
