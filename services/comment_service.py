from db_connector import db, Comment, Post
from helpers import current_user
from flask import abort


def create_comment(post_id: int, content: str) -> Comment:
    post = Post.query.get_or_404(post_id)
    comment = Comment(content=content, author=current_user(), post=post)
    db.session.add(comment)
    db.session.commit()
    return comment


def get_comment_or_404(comment_id: int) -> Comment:
    return Comment.query.get_or_404(comment_id)


def delete_comment(comment: Comment) -> None:
    db.session.delete(comment)
    db.session.commit()


def is_comment_owner_or_post_owner(comment: Comment) -> bool:
    user = current_user()
    return user and (comment.author.id == user.id or comment.post.author.id == user.id)
