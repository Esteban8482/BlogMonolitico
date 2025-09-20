"""
Post Service

Desacoplar la lógica de autenticación de usuarios de la aplicación con los endpoints

- Crear post
- Obtener post por ID
- Actualizar post
- Eliminar post
- Obtener posts de un usuario
"""

from db_connector import db, Post, User
from typing import Optional, List


def create_post(title: str, content: str, author_id: int) -> Post:
    post = Post(title=title, content=content, user_id=author_id)
    db.session.add(post)
    db.session.commit()
    return post


def get_post(post_id: int) -> Optional[Post]:
    return db.session.get(Post, post_id)


def get_post_or_404(post_id: int) -> Post:
    post = get_post(post_id)
    if post is None:
        from flask import abort

        abort(404)
    return post


def update_post(post: Post, title: str, content: str) -> None:
    post.title = title
    post.content = content
    db.session.commit()


def delete_post(post: Post) -> None:
    db.session.delete(post)
    db.session.commit()


def get_user_posts(user: User) -> List[Post]:
    return Post.query.filter_by(author=user).order_by(Post.created_at.desc()).all()


def get_user_posts_by_id(user_id: int) -> List[Post]:
    return Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
