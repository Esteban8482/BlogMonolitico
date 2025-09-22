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
from services.post_service import get_post_or_404

comment_api = Blueprint("comment", __name__)

# =============================
# RUTAS DE COMENTARIOS
# =============================


@comment_api.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id: int):
    post = get_post_or_404(post_id)
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

    post_id = int(comment.post_id)
    delete_comment_service(comment)
    flash("Comentario eliminado", "info")
    return redirect(url_for("post.post_detail", post_id=post_id))


