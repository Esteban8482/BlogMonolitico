"""
Post Service

Desacoplar la lógica de autenticación de usuarios de la aplicación con los endpoints

- Crear post
- Obtener post por ID
- Actualizar post
- Eliminar post
- Obtener posts de un usuario
"""

from db_connector import Post
from typing import Optional, List
from datetime import datetime


def create_post(title: str, content: str, author_id: str, author_username: str) -> Post:
    post = Post(
        id=None,
        title=title,
        content=content,
        user_id=author_id,
        username=author_username,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    post.save_to_db()
    return post


def get_post(post_id: str) -> Optional[Post]:
    return Post.get_by_id(post_id)


def get_posts_service(limit: int, title: str) -> List[Post]:
    return Post.get_posts(limit, title)


def update_post(post: Post, title: str, content: str) -> Post:
    post.title = title
    post.content = content
    post.updated_at = datetime.utcnow()
    post.save_to_db()
    return post


def delete_post(post: Post) -> None:
    post.delete_from_db()


def get_user_posts(user_id: str) -> List[Post]:
    return Post.get_user_posts(user_id)


def exists_post(post_id: str) -> bool:
    return Post.exists_by_id(post_id)
