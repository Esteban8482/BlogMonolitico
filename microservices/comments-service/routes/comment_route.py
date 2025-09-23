from flask import Blueprint, request, jsonify
from services import comment_service

bp = Blueprint("comments", __name__)


def _user_id():
    return request.headers.get("X-User-Id")


@bp.post("/comments")
def create_comment():
    uid = _user_id()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    post_id = str(data.get("post_id") or "").strip()
    content = (data.get("content") or "").strip()
    username = (data.get("username") or "").strip()
    
    if not post_id or not content or not username:
        return jsonify({"error": "post_id y content son requeridos"}), 400

    c = comment_service.create_comment(
        user_id=str(uid), post_id=post_id, content=content, username=username
    )

    return {
        "id": c["id"],
        "post_id": c["post_id"],
        "user_id": c["user_id"],
        "content": c["content"],
        "created_at": c.get("created_at"),
        "username": c.get("username"),
    }, 201


@bp.get("/comments/<string:comment_id>")
def get_comment(comment_id: str):
    c = comment_service.get_comment(comment_id)
    if c.get("is_deleted"):
        return jsonify({"error": "Comment deleted"}), 404
    return {
        "id": c["id"],
        "post_id": c["post_id"],
        "user_id": c["user_id"],
        "content": c["content"],
        "created_at": c.get("created_at"),
        "username": c.get("username"),
    }


# @bp.patch("/comments/<string:comment_id>")
# def update_comment(comment_id: str):
#     uid = _user_id()
#     if not uid:
#         return jsonify({"error": "Unauthorized"}), 401

#     payload = request.get_json(silent=True) or {}
#     content = payload.get("content")

#     updated, err = comment_service.update_comment(
#         comment_id, user_id=str(uid), content=content
#     )
#     if err == "forbidden":
#         return jsonify({"error": "Forbidden"}), 403
#     if err == "invalid":
#         return jsonify({"error": "Invalid content"}), 400

#     return {
#         "id": updated["id"],
#         "post_id": updated["post_id"],
#         "user_id": updated["user_id"],
#         "content": updated["content"],
#         "created_at": updated.get("created_at"),
#     }


@bp.delete("/comments/<string:comment_id>")
def delete_comment(comment_id: str):
    uid = _user_id()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    role = request.headers.get("X-User-Role")
    deleted, err = comment_service.delete_comment(
        comment_id, requester_id=str(uid), role=role
    )
    if err == "forbidden":
        return jsonify({"error": "Forbidden"}), 403
    return {"status": "deleted"}


@bp.get("/comments")
def list_comments():
    post_id = (request.args.get("post_id") or "").strip()
    user_id = request.args.get("user_id")
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    try:
        page = int(request.args.get("page", 1))
    except Exception:
        page = 1
    try:
        per_page = min(int(request.args.get("per_page", 10)), 100)
    except Exception:
        per_page = 10

    res = comment_service.list_comments(
        post_id=post_id or None,
        user_id=user_id or None,
        include_deleted=include_deleted,
        page=page,
        per_page=per_page,
    )

    return res
