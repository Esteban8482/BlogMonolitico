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

from db_connector import Post
from helpers import current_user, login_required
from services.post_service import (
    create_post as create_post_service,
    get_post_or_404,
    update_post,
    delete_post as delete_post_service,
)

post_api = Blueprint("post", __name__)

# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================


@post_api.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Título y contenido requeridos", "danger")
        else:
            post = create_post_service(title, content, current_user().id)
            flash("Publicación creada", "success")
            return redirect(url_for("post.post_detail", post_id=post.id))

    return render_template("create_post.html")


def _require_post_owner(post: Post):
    if not current_user() or post.author.id != current_user().id:
        abort(403)


@post_api.route("/post/<int:post_id>")
def post_detail(post_id: int):
    post = get_post_or_404(post_id)
    return render_template("post_detail.html", post=post, user=current_user())


@post_api.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    post = get_post_or_404(post_id)
    _require_post_owner(post)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Campos requeridos", "danger")
        else:
            update_post(post, title, content)
            flash("Publicación actualizada", "success")
            return redirect(url_for("post.post_detail", post_id=post.id))

    return render_template("edit_post.html", post=post)


@post_api.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post = get_post_or_404(post_id)
    _require_post_owner(post)
    delete_post_service(post)

    flash("Publicación eliminada", "info")
    return redirect(url_for("index"))
