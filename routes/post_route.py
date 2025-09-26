from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
import markdown

from services.comment_service import list_comments
from services.post_service import (
    create_post as create_post_service,
    get_post,
    update_post,
    delete_post_by_id,
)
from helpers import current_user, login_required


post_api = Blueprint("post", __name__)

# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================


@post_api.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post = create_post_service(
            current_user().username,
            request.form.get("title", "").strip(),
            request.form.get("content", "").strip(),
        )

        if not post:
            flash("Error al crear la publicación", "danger")
            return redirect(url_for("post.create_post"))

        return redirect(url_for("post.post_detail", post_id=post.id))

    return render_template("create_post.html")


@post_api.route("/post/<string:post_id>")
@login_required
def post_detail(post_id: str):
    post = get_post(post_id)

    if not post:
        flash("Error al obtener la publicación", "danger")
        abort(400)

    comments = []

    try:
        comments = list_comments(post.id)

        if comments is None:
            comments = []
            flash("Error al obtener los comentarios", "danger")
    except:
        flash("Error al obtener los comentarios", "danger")

    markdown_content = markdown.markdown(
        post.content, extensions=["extra", "codehilite", "tables"]
    )
    return render_template(
        "post_detail.html",
        post=post,
        user=current_user(),
        comments=comments,
        markdown_content=markdown_content,
    )


@post_api.route("/post/<string:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: str):
    if request.method == "GET":
        post = get_post(post_id)

        if not post:
            flash("Error al obtener la publicación", "danger")
            abort(400)

        return render_template("edit_post.html", post=post)
    elif request.method == "POST":
        post = update_post(
            post_id,
            request.form.get("title", "").strip(),
            request.form.get("content", "").strip(),
        )

        if not post:
            flash("Error al editar la publicación", "danger")
            return redirect(url_for("post.edit_post", post_id=post_id))

        flash("Publicación editada", "success")
        return redirect(url_for("post.post_detail", post_id=post.id))


@post_api.route("/post/<string:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: str):
    success = delete_post_by_id(post_id)

    if not success:
        flash("Error al eliminar la publicación", "danger")
        return redirect(url_for("post.post_detail", post_id=post_id))

    flash("Publicación eliminada", "success")
    return redirect(url_for("index"))
