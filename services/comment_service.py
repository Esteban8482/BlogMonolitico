"""
Comment Service

Desacoplar la lógica de autenticación de usuarios de la aplicación con los endpoints

- Agregar comentario
- Obtener comentario por ID
- Eliminar comentario
- Verificar si el comentario pertenece al autor del post
"""

from db_connector import db, Comment
from helpers import current_user
from flask import abort


def create_comment(post_id: int, content: str) -> Comment:
    comment = Comment(content=content, author=current_user(), post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    return comment


def get_post_comments(post_id: int) -> list[Comment]:
    return Comment.query.filter_by(post_id=post_id).all()


def get_comment_or_404(comment_id: int) -> Comment:
    return Comment.query.get_or_404(comment_id)


def delete_comment(comment: Comment) -> None:
    db.session.delete(comment)
    db.session.commit()


def is_comment_owner_or_post_owner(comment: Comment) -> bool:
    user = current_user()
    return user and (comment.author.id == user.id or comment.post.author.id == user.id)
