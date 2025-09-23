from typing import Optional, Tuple
from datetime import datetime
from flask import abort
from db_connector import get_db
from google.cloud import firestore

COLL = "comments"

def create_comment(user_id: str, post_id: str, content: str):
    content = (content or "").strip()
    if not content:
        abort(400, "Comentario vacío")

    db = get_db()
    doc_ref = db.collection(COLL).document()
    doc_ref.set({
        "user_id": str(user_id),
        "post_id": str(post_id),
        "content": content,
        "created_at": firestore.SERVER_TIMESTAMP,
        "is_deleted": False,
    })

    snap = doc_ref.get()
    data = snap.to_dict()
    return {"id": doc_ref.id, **data}

def list_comments(
    post_id: Optional[str],
    user_id: Optional[str],
    include_deleted: bool,
    page: int,
    per_page: int,
):
    db = get_db()
    q = db.collection(COLL)

    if post_id:
        q = q.where("post_id", "==", str(post_id))
    if user_id:
        q = q.where("user_id", "==", str(user_id))
    if not include_deleted:
        q = q.where("is_deleted", "==", False)

    q = q.order_by("created_at", direction=firestore.Query.DESCENDING)


    snaps = q.limit(per_page).stream()
    items = []
    for s in snaps:
        d = s.to_dict()
        items.append({"id": s.id, **d})

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": len(items),
    }

def get_comment(comment_id: str):
    db = get_db()
    snap = db.collection(COLL).document(str(comment_id)).get()
    if not snap.exists:
        abort(404, "Comentario no encontrado")
    d = snap.to_dict()
    return {"id": snap.id, **d}

def update_comment(comment_id: str, user_id: str, content: Optional[str]) -> Tuple[Optional[dict], Optional[str]]:
    db = get_db()
    doc_ref = db.collection(COLL).document(str(comment_id))
    snap = doc_ref.get()
    if not snap.exists:
        abort(404)

    data = snap.to_dict()
    if data["user_id"] != str(user_id):
        return None, "forbidden"

    if content is not None:
        content = content.strip()
        if not content:
            return None, "invalid"
        doc_ref.update({"content": content})

    snap = doc_ref.get()
    return {"id": snap.id, **snap.to_dict()}, None

def delete_comment(comment_id: str, requester_id: str, role: Optional[str]):
    db = get_db()
    doc_ref = db.collection(COLL).document(str(comment_id))
    snap = doc_ref.get()
    if not snap.exists:
        abort(404)

    data = snap.to_dict()
    if data["user_id"] != str(requester_id) and role != "moderator":
        return None, "forbidden"

    doc_ref.update({"is_deleted": True})

    snap = doc_ref.get()
    return {"id": snap.id, **snap.to_dict()}, None
