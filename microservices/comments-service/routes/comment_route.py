from flask import Blueprint, request, jsonify
from db_connector import db
from models import Comment

bp = Blueprint("comments", __name__)

def _user_id():
    return request.headers.get("X-User-Id")

@bp.post("/comments")
def create_comment():
    uid = _user_id()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    try:
        post_id = int(data.get("post_id", 0))
    except Exception:
        return jsonify({"error": "post_id inválido"}), 400

    content = (data.get("content") or "").strip()
    if not post_id or not content:
        return jsonify({"error": "post_id y content son requeridos"}), 400

    c = Comment(post_id=post_id, user_id=str(uid), content=content)
    db.session.add(c)
    db.session.commit()
    return {
        "id": c.id,
        "post_id": c.post_id,
        "user_id": c.user_id,
        "content": c.content,
        "created_at": c.created_at.isoformat(),
    }, 201

@bp.get("/comments/<int:comment_id>")
def get_comment(comment_id: int):
    c = Comment.query.get(comment_id)
    if not c:
        return jsonify({"error": "Not Found"}), 404
    return {
        "id": c.id,
        "post_id": c.post_id,
        "user_id": c.user_id,
        "content": c.content,
        "created_at": c.created_at.isoformat(),
    }

@bp.delete("/comments/<int:comment_id>")
def delete_comment(comment_id: int):
    uid = _user_id()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    c = Comment.query.get(comment_id)
    if not c:
        return jsonify({"error": "Not Found"}), 404

    role = request.headers.get("X-User-Role")
    if str(c.user_id) != str(uid) and role != "moderator":
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(c)
    db.session.commit()
    return {"status": "deleted"}

@bp.get("/comments")
def list_comments():
    try:
        post_id = int(request.args.get("post_id", "0"))
    except Exception:
        post_id = 0

    if not post_id:
        return {"items": [], "total": 0, "page": 1, "per_page": 0}

    q = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc())
    rows = q.all()

    items = [{
        "id": c.id,
        "post_id": c.post_id,
        "user_id": c.user_id,
        "content": c.content,
        "created_at": c.created_at.isoformat(),
    } for c in rows]

    return {
        "items": items,
        "total": len(items),
        "page": 1,
        "per_page": len(items),
    }
