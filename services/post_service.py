from db_connector import db, Post
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
