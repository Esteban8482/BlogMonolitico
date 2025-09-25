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
from dtos import PostDto
from log import logger

_TIMEOUT = 5


def _headers_for_user(user_id: str = None):
    header_id = user_id

    if user_id is None:
        header_id = current_user().id

    return {"X-User-Id": str(header_id)}


def create_post(username: str, title: str, content: str) -> Optional[PostDto]:
    """
    Crear un nuevo post en el microservicio de Post.

    Parameters:
        username (str): El username del usuario que crea el post.
        title (str): El título del post.
        content (str): El contenido del post.

    Returns:
        Optional[PostDto]: El post creado, o None si no se pudo crear el post.
    """
    try:
        post_rq = requests.post(
            f"{ServicesConfig.POST_SERVICE_URL}/post/new",
            headers=_headers_for_user(),
            json={
                "title": title.strip(),
                "content": content.strip(),
                "username": username,
            },
            timeout=_TIMEOUT,
        )

        post = PostDto.from_json(post_rq.json()["data"])
        return post
    except:
        return None


def get_post(post_id: str) -> Optional[PostDto]:
    """
    Obtener un post por su ID en el microservicio de Post.

    Parameters:
        post_id (str): El ID del post a obtener.

    Returns:
        Optional[PostDto]: El post obtenido, o None si no se pudo obtener el post.
    """
    try:
        post_rq = requests.get(
            f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}",
            headers=_headers_for_user(),
            timeout=_TIMEOUT,
        )
        return PostDto.from_json(post_rq.json()["data"])
    except:
        return None


def update_post(post_id: str, title: str, content: str) -> Optional[PostDto]:
    """
    Actualizar un post en el microservicio de Post.

    Parameters:
        post_id (str): El ID del post a actualizar.
        title (str): El título del post.
        content (str): El contenido del post.

    Returns:
        Optional[PostDto]: El post actualizado, o None si no se pudo actualizar el post.
    """
    try:
        post_req = requests.post(
            f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}/edit",
            headers=_headers_for_user(),
            json={
                "title": title.strip(),
                "content": content.strip(),
            },
            timeout=_TIMEOUT,
        )

        return PostDto.from_json(post_req.json()["data"])
    except:
        return None


def delete_post_by_id(post_id: str) -> bool:
    """
    Eliminar un post en el microservicio de Post.

    Parameters:
        post_id (str): El ID del post a eliminar.

    Returns:
        bool: True si se pudo eliminar el post, False en caso contrario.
    """
    try:
        post_req = requests.post(
            f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}/delete",
            headers=_headers_for_user(),
            timeout=_TIMEOUT,
        )

        return post_req.status_code >= 200 and post_req.status_code < 300
    except:
        return False


def get_user_posts(user_id) -> Optional[List[PostDto]]:
    """
    Obtener los posts de un usuario en el microservicio de Post.

    Parameters:
        user_id (str): El ID del usuario a obtener los posts.

    Returns:
        Optional[List[PostDto]]: La lista de posts del usuario, o None si no se pudo obtener los posts.
    """
    try:
        post_req = requests.get(
            f"{ServicesConfig.POST_SERVICE_URL}/post/user/{user_id}",
            timeout=_TIMEOUT,
        )

        data = post_req.json()["data"]

        if len(data) == 0:
            return []

        return [PostDto.from_json(post) for post in data]
    except:
        return None


def get_post_limit(limit: int, title: str) -> Optional[List[PostDto]]:
    """
    Obtener los posts de un usuario en el microservicio de Post.

    Parameters:
        user_id (str): El ID del usuario a obtener los posts.

    Returns:
        Optional[List[PostDto]]: La lista de posts del usuario, o None si no se pudo obtener los posts.
    """
    try:
        url = f"{ServicesConfig.POST_SERVICE_URL}/post/limit/{limit}?title={title}"
        logger.info(f"======== Obteniendo posts ========\n{url=}\n")

        post_req = requests.get(
            url,
            timeout=_TIMEOUT,
        )

        data = post_req.json()["data"]

        if len(post_req.json()["data"]) == 0:
            return []

        return [PostDto.from_json(post) for post in post_req.json()["data"]]
    except Exception as e:
        logger.error(f"======== Error al obtener los posts ========\n{e}\n")
        return None
