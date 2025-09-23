from dtos.PostDto import PostDto

"""
Post Service

Desacoplar la lógica de autenticación de usuarios de la aplicación con los endpoints

- Crear post
- Obtener post por ID
- Actualizar post
- Eliminar post
- Obtener posts de un usuario

Llamar al microservicio de Post
"""

from typing import Optional, List
import requests

from config import ServicesConfig
from helpers import current_user
from dtos import UserDto


def _headers_for_user(user_id: str = None):
    header_id = user_id

    if user_id is None:
        header_id = current_user().id

    return {"X-User-Id": str(header_id)}


def create_user_profile(user_id: str, username: str) -> Optional[UserDto]:
    """
    Crear un nuevo perfil de usuario en el microservicio de Usuario.

    Parameters:
        user_id (str): El ID del usuario a crear el perfil.
        username (str): El username del usuario a crear el perfil.

    Returns:
        Optional[UserDto]: El perfil del usuario creado, o None si no se pudo crear el perfil.
    """
    try:
        req = requests.post(
            f"{ServicesConfig.USER_SERVICE_URL}/u/new",
            json={"id": str(user_id), "username": username.strip()},
        )

        return UserDto.from_json(req.json()["data"])
    except:
        return None


def get_user_profile(username: str) -> Optional[UserDto]:
    """
    Obtener el perfil de un usuario en el microservicio de Usuario.

    Parameters:
        username (str): El username del usuario a obtener el perfil.

    Returns:
        Optional[UserDto]: El perfil del usuario, o None si no se pudo obtener el perfil.
    """
    try:
        req = requests.get(
            f"{ServicesConfig.USER_SERVICE_URL}/u/{username}",
            headers=_headers_for_user(),
        )

        return UserDto.from_json(req.json()["data"])
    except:
        return None


def update_user_profile(username: str, bio: str) -> bool:
    """
    Actualizar el perfil de un usuario en el microservicio de Usuario.

    Parameters:
        username (str): El username del usuario a actualizar el perfil.
        bio (str): La biografia del usuario.

    Returns:
        Optional[UserDto]: El perfil del usuario actualizado, o None si no se pudo actualizar el perfil.
    """
    try:
        req = requests.post(
            f"{ServicesConfig.USER_SERVICE_URL}/u/{username}",
            headers=_headers_for_user(),
            json={"bio": bio.strip()},
        )

        return req.status_code >= 200 and req.status_code < 300
    except:
        return False
