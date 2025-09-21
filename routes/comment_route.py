from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)

from helpers import current_user, login_required
from services.comment_service import (
    create_comment,
    get_comment_or_404,
    delete_comment as delete_comment_service,
    is_comment_owner_or_post_owner,
)
from config import ServicesConfig
import requests
from dtos import PostDto

comment_api = Blueprint("comment", __name__)

# =============================
# RUTAS DE COMENTARIOS
# =============================


@comment_api.route("/post/<string:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id: str):
    post_req = requests.get(
        f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}",
        headers={"X-User-ID": str(current_user().id)},
    )

    if not (post_req.status_code >= 200 and post_req.status_code < 300):
        flash(post_req.json()["message"], "danger")
        abort(post_req.status_code)

    try:
        post = PostDto.from_json(post_req.json()["post"])
    except:
        flash("Error al obtener la publicación", "danger")
        abort(500)

    content = request.form.get("content", "").strip()

    if not content:
        flash("Comentario vacío", "danger")
    else:
        create_comment(post_id, content)
        flash("Comentario agregado", "success")

    return redirect(url_for("post.post_detail", post_id=post.id))


@comment_api.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id: int):
    comment = get_comment_or_404(comment_id)

    if not is_comment_owner_or_post_owner(comment):
        abort(403)

    post_id = comment.post_id
    delete_comment_service(comment)
    flash("Comentario eliminado", "info")
    return redirect(url_for("post.post_detail", post_id=post_id))
