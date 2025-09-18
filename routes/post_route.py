from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connector import Post, db
from helpers import current_user, login_required

post_route = Blueprint("post", __name__)

# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================


@post_route.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Título y contenido requeridos", "danger")
        else:
            post = Post(title=title, content=content, author=current_user())
            db.session.add(post)
            db.session.commit()
            flash("Publicación creada", "success")
            return redirect(url_for("post.post_detail", post_id=post.id))
    return render_template("create_post.html")


def _require_post_owner(post: Post):
    if not current_user() or post.author.id != current_user().id:
        abort(403)


@post_route.route("/post/<int:post_id>")
def post_detail(post_id: int):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post, user=current_user())


@post_route.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    _require_post_owner(post)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Campos requeridos", "danger")
        else:
            post.title = title
            post.content = content
            db.session.commit()
            flash("Publicación actualizada", "success")
            return redirect(url_for("post.post_detail", post_id=post.id))
    return render_template("edit_post.html", post=post)


@post_route.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    _require_post_owner(post)
    db.session.delete(post)
    db.session.commit()
    flash("Publicación eliminada", "info")
    return redirect(url_for("index"))
