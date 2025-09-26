# services/comment_service.py (MONOLITO) — llama por HTTP al microservicio
import os
import requests
from flask import abort
from helpers import current_user
from services.post_service import get_post
from log import logger

COMMENTS_BASE = os.getenv("COMMENTS_BASE", "http://localhost:8091/v1")


class CommentDto:
    def __init__(self, id, post_id, user_id, content, created_at, username):
        self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at
        self.username = username


def _headers_for_user(user):
    return {"X-User-Id": str(user.id)}


def create_comment(post_id: str, content: str, username: str) -> CommentDto | None:
    post = get_post(str(post_id))

    if not post:
        logger.error(f"======== Error al obtener el post ========\n{post_id=}\n")
        return None

    user = current_user()
    if not user:
        logger.error(f"======== Error al obtener el usuario ========\n")
        return None

    try:
        r = requests.post(
            f"{COMMENTS_BASE}/comments",
            json={"post_id": post_id, "content": content, "username": username},
            headers=_headers_for_user(user),
            timeout=5,
        )

        logger.info(f"======== create_comment ========\n{r.status_code=}\n")

        if r.status_code == 201:
            d = r.json()
            return CommentDto(
                d["id"],
                d["post_id"],
                d["user_id"],
                d["content"],
                d["created_at"],
                d["username"],
            )

            logger.error(
                f"======== create_comment ========\n{r.status_code=} {r.json()}\n"
            )
        elif r.status_code == 401:
            return None
    except Exception as e:
        logger.error(f"======== Error create_comment ========\n{e}\n")
        return None


def get_comment_or_404(comment_id: int) -> CommentDto | None:
    try:
        r = requests.get(f"{COMMENTS_BASE}/comments/{comment_id}", timeout=5)

        logger.info(f"======== get_comment_or_404 ========\n{r.status_code=}\n")

        if r.status_code == 200:
            d = r.json()
            return CommentDto(
                d["id"],
                d["post_id"],
                d["user_id"],
                d["content"],
                d["created_at"],
                d["username"],
            )

            logger.error(
                f"======== get_comment_or_404 ========\n{r.status_code=} {r.json()}\n"
            )
        elif r.status_code == 404:
            return None
    except Exception as e:
        logger.error(f"======== Error get_comment_or_404 ========\n{e}\n")
        return None

    logger.info(f"======== get_comment_or_404 ========\n{r.status_code=}\n")


def delete_comment(comment: CommentDto) -> bool:
    user = current_user()
    if not user:
        logger.error("======== Error al obtener el usuario ========")
        return False

    # Si el usuario es dueño del post, lo tratamos como "moderator"
    post = get_post(str(comment.post_id))

    if not post:
        logger.error("======== Error al obtener el post ========")
        return False

    is_post_owner = post.user_id == user.id

    headers = _headers_for_user(user)
    if is_post_owner:
        headers["X-User-Role"] = "moderator"

    try:
        r = requests.delete(
            f"{COMMENTS_BASE}/comments/{comment.id}", headers=headers, timeout=5
        )
    except Exception as e:
        logger.error(f"======== Error delete_comment ========\n{e}\n")
        return False

    logger.info(f"======== delete_comment ========\n{r.status_code=}\n")

    if r.status_code in (200, 204):
        return True
    else:
        return False


def is_comment_owner_or_post_owner(comment: CommentDto) -> bool:
    user = current_user()
    if not user:
        logger.error("======== Error al obtener el usuario ========")
        return False

    if str(comment.user_id) == str(user.id):
        logger.info("======== is_comment_owner_or_post_owner ========\n")
        return True

    post = get_post(str(comment.post_id))

    if not post:
        logger.error("======== Error al obtener el post ========")
        return False

    return (post is not None) and (str(post.user_id) == str(user.id))


def list_comments(post_id: str) -> list[CommentDto] | None:
    url = f"{COMMENTS_BASE}/comments"

    logger.info(f"======== list_comments ========\n{url=}\n{post_id=}\n")

    try:
        r = requests.get(
            f"{COMMENTS_BASE}/comments", params={"post_id": post_id}, timeout=5
        )
    except Exception as e:
        logger.error(f"======== Error list_comments ========\n{e}\n")
        return None

    logger.info(f"======== list_comments ========\n{r.status_code=}\n")

    if r.status_code != 200:
        return None

    data = r.json()
    items = data.get("items", [])
    return [
        CommentDto(
            d["id"],
            d["post_id"],
            d["user_id"],
            d["content"],
            d["created_at"],
            d["username"],
        )
        for d in items
    ]
