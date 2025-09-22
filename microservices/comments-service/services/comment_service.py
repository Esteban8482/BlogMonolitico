from typing import Optional, Tuple
from sqlalchemy import desc
from db_connector import db
from models import Comment


def create_comment(user_id: str, post_id: str, content: str) -> Comment:
    c = Comment(user_id=user_id, post_id=post_id, content=content)
    db.session.add(c)
    db.session.commit()
    return c


def list_comments(post_id: Optional[str], user_id: Optional[str], include_deleted: bool, page: int, per_page: int):
    q = Comment.query
    if post_id:
        q = q.filter(Comment.post_id == post_id)
    if user_id:
        q = q.filter(Comment.user_id == user_id)
    if not include_deleted:
        q = q.filter(Comment.is_deleted == False)  # noqa: E712
    q = q.order_by(desc(Comment.created_at))
    return q.paginate(page=page, per_page=per_page, error_out=False)


def get_comment(comment_id: int) -> Comment:
    return Comment.query.get_or_404(comment_id)


def update_comment(comment_id: int, user_id: str, content: Optional[str]) -> Tuple[Optional[Comment], Optional[str]]:
    c = Comment.query.get_or_404(comment_id)
    if c.user_id != user_id:
        return None, "forbidden"
    if content is not None:
        content = content.strip()
        if not content:
            return None, "invalid"
        c.content = content
        db.session.commit()
    return c, None


def delete_comment(comment_id: int, requester_id: str, role: Optional[str]) -> Tuple[Optional[Comment], Optional[str]]:
    c = Comment.query.get_or_404(comment_id)
    if c.user_id != requester_id and role != "moderator":
        return None, "forbidden"
    c.is_deleted = True
    db.session.commit()
    return c, None