from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)

from helpers import current_user, login_required
from services.post_service import get_user_posts
from services.user_service import get_user_profile, update_user_profile


user_api = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_api.route("/u/<username>", methods=["GET", "POST"])
@login_required
def profile(username: str):
    if request.method == "GET":
        user = get_user_profile(username)

        if not user:
            flash("Error al obtener el perfil", "error")
            abort(400)

        posts = get_user_posts(user.id)

        if posts is None:
            flash("Error al obtener las publicaciones", "error")
            posts = []

        return render_template(
            "profile.html",
            profile_user=user,
            posts=posts,
            user=current_user(),
        )
    elif request.method == "POST":
        user = update_user_profile(username, request.form.get("bio", ""))

        if not user:
            flash("Error al actualizar el perfil", "error")
            return redirect(url_for("user.profile", username=username))

        flash("Perfil actualizado", "success")
        return redirect(url_for("user.profile", username=username))
