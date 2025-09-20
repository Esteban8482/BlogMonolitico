"""
User Service

Desacoplar la lógica de autenticación de usuarios de la aplicación con los endpoints

- Obtener usuario por ID o nombre
- Actualizar bio
- Verificar si el usuario es el propietario de un post
"""

from db_connector import db, User
from typing import Optional, List


def get_user_or_404(user_id_or_name: int | str) -> Optional[User]:
    if isinstance(user_id_or_name, int):
        return User.query.get(user_id_or_name)

    return User.query.filter(User.username == user_id_or_name).first()


def update_user_bio(user: User, bio: str) -> User:
    user.bio = bio
    db.session.commit()
    return user


def create_user(id: int, username: str) -> User:
    user = User(
        id=id,
        username=username,
    )

    db.session.add(user)
    db.session.commit()
    return user


def exists_user(id: int, username: str) -> bool:
    return User.query.filter((User.id == id) | (User.username == username)).first()
