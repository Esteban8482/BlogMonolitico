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
from services.user_service import get_user_or_404, update_user_bio, is_user_owner
from services.post_service import get_user_posts

user_api = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_api.route("/u/<username>", methods=["GET", "POST"])
@login_required
def profile(username: str):
    user = get_user_or_404(username)

    if request.method == "POST":
        if not is_user_owner(user, current_user()):
            abort(403)

        bio = request.form.get("bio", "")
        update_user_bio(user, bio)
        flash("Perfil actualizado", "success")

        return redirect(url_for("user.profile", username=user.username))

    posts = get_user_posts(user)

    return render_template(
        "profile.html", profile_user=user, posts=posts, user=current_user()
    )
