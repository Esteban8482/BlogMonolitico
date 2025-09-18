from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connector import User, Post, Comment
from db_connector import db
from helpers import current_user, login_required

user_route = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_route.route("/u/<username>", methods=["GET", "POST"])
def profile(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == "POST":
        if not current_user() or current_user().id != user.id:
            abort(403)
        bio = request.form.get("bio", "")
        user.bio = bio
        db.session.commit()
        flash("Perfil actualizado", "success")
        return redirect(url_for("user.profile", username=user.username))

    posts = Post.query.filter_by(author=user).order_by(Post.created_at.desc()).all()

    return render_template(
        "profile.html", profile_user=user, posts=posts, user=current_user()
    )
