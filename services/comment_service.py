# services/comment_service.py (MONOLITO) — llama por HTTP al microservicio
import os
import requests
from flask import abort
from helpers import current_user
from services.post_service import get_post_or_404

COMMENTS_BASE = os.getenv("COMMENTS_BASE", "http://localhost:8091/v1")

class CommentDto:
    def __init__(self, id, post_id, user_id, content, created_at):
        self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at

def _headers_for_user(user):
    return {"X-User-Id": str(user.id)}

def create_comment(post_id: int, content: str) -> CommentDto:
    # Igual que antes: verificas que el post exista (regla de negocio local)
    get_post_or_404(post_id)

    user = current_user()
    if not user:
        abort(401)

    r = requests.post(
        f"{COMMENTS_BASE}/comments",
        json={"post_id": post_id, "content": content},
        headers=_headers_for_user(user),
        timeout=5,
    )
    if r.status_code == 201:
        d = r.json()
        return CommentDto(d["id"], d["post_id"], d["user_id"], d["content"], d["created_at"])
    elif r.status_code == 401:
        abort(401)
    elif r.status_code == 400:
        abort(400, r.json().get("error", "Invalid"))
    else:
        abort(502, f"comments service error: {r.status_code}")

def get_comment_or_404(comment_id: int) -> CommentDto:
    r = requests.get(f"{COMMENTS_BASE}/comments/{comment_id}", timeout=5)
    if r.status_code == 200:
        d = r.json()
        return CommentDto(d["id"], d["post_id"], d["user_id"], d["content"], d["created_at"])
    elif r.status_code == 404:
        abort(404)
    else:
        abort(502, f"comments service error: {r.status_code}")

def delete_comment(comment: CommentDto) -> None:
    user = current_user()
    if not user:
        abort(401)

    # Si el usuario es dueño del post, lo tratamos como "moderator"
    post = get_post_or_404(int(comment.post_id))
    is_post_owner = (post.author.id == user.id)

    headers = _headers_for_user(user)
    if is_post_owner:
        headers["X-User-Role"] = "moderator"

    r = requests.delete(f"{COMMENTS_BASE}/comments/{comment.id}", headers=headers, timeout=5)
    if r.status_code in (200, 204):
        return
    elif r.status_code == 403:
        abort(403)
    elif r.status_code == 404:
        abort(404)
    else:
        abort(502, f"comments service error: {r.status_code}")

def is_comment_owner_or_post_owner(comment: CommentDto) -> bool:
    user = current_user()
    if not user:
        return False

    if str(comment.user_id) == str(user.id):
        return True

    post = get_post_or_404(int(comment.post_id))
    return post and (post.author.id == user.id)

def list_comments(post_id: int) -> list[CommentDto]:
    r = requests.get(f"{COMMENTS_BASE}/comments", params={"post_id": post_id}, timeout=5)
    if r.status_code != 200:
        abort(502, f"comments service error: {r.status_code}")
    data = r.json()
    items = data.get("items", [])
    return [CommentDto(d["id"], d["post_id"], d["user_id"], d["content"], d["created_at"]) for d in items]