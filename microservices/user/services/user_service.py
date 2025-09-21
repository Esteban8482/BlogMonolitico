"""
User Service

Desacoplar la lógica de autenticación de usuarios de la aplicación con los endpoints

- Obtener usuario por ID o nombre
- Actualizar bio
- Verificar si el usuario es el propietario de un post
"""

from db_connector import User
from typing import Optional, List
from datetime import datetime


def get_user_or_404(user_id_or_name: str) -> Optional[User]:
    return User.get_by_id_or_username(user_id_or_name, user_id_or_name)


def update_user_bio(user: User, bio: str) -> User:
    user_db = User.get_by_id(user.id)
    user_db.bio = bio
    user_db.save_to_db()
    return user_db


def create_user(user_id: str, username: str) -> User:
    user = User(
        id=user_id,
        username=username,
        bio="",
        created_at=datetime.now(),
    )

    user.save_to_db()

    return user


def exists_user(user_id: str, username: str) -> bool:
    return User.exists_by_username_or_id(user_id, username)
