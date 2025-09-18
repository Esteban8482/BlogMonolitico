from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connector import User, Post, Comment
from db_connector import db
from helpers import current_user, login_required

comment_route = Blueprint("comment", __name__)

# =============================
# RUTAS DE COMENTARIOS
# =============================


@comment_route.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id: int):
    post = Post.query.get_or_404(post_id)
    content = request.form.get("content", "").strip()
    if not content:
        flash("Comentario vacío", "danger")
    else:
        comment = Comment(content=content, author=current_user(), post=post)
        db.session.add(comment)
        db.session.commit()
        flash("Comentario agregado", "success")
    return redirect(url_for("post.post_detail", post_id=post.id))


@comment_route.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id: int):
    comment = Comment.query.get_or_404(comment_id)
    if (
        comment.author.id != current_user().id
        and comment.post.author.id != current_user().id
    ):
        abort(403)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    flash("Comentario eliminado", "info")
    return redirect(url_for("post.post_detail", post_id=post_id))
