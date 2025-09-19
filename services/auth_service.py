# services/auth_service.py
from db_connector import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional


def register_user(username: str, email: str, password: str) -> Optional[User]:
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return None  # Usuario ya existe

    user = User(username=username, email=email)
    user.password_hash = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(username_or_email: str, password: str) -> Optional[User]:
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email.lower())
    ).first()

    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def get_user_by_id(user_id: int) -> Optional[User]:
    return db.session.get(User, user_id)
