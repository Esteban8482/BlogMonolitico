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
import requests

from helpers import current_user, login_required
from dtos import UserDto, PostDto
from config import ServicesConfig

user_api = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_api.route("/u/<username>", methods=["GET", "POST"])
@login_required
def profile(username: str):
    if request.method == "GET":
        # micro-servicio de usuario
        user_req = requests.get(
            f"{ServicesConfig.USER_SERVICE_URL}/u/{username}",
            headers={"X-User-ID": str(current_user().id)},
        )

        if user_req.status_code != 200:
            flash("Error al obtener el perfil", "error")
            abort(404)

        try:
            user = UserDto.from_json(user_req.json()["data"])
        except Exception as e:
            flash("Error al obtener el perfil", "error")
            abort(404)

        posts_req = requests.get(
            f"{ServicesConfig.POST_SERVICE_URL}/post/user/{user.id}",
            headers={"X-User-ID": str(current_user().id)},
        )

        if not (posts_req.status_code >= 200 and posts_req.status_code < 300):
            message = (
                posts_req.json()["message"]
                if "message" in posts_req.json()
                else "Error al obtener las publicaciones"
            )
            flash(message, "error")

        posts = []

        try:
            posts = [PostDto.from_json(post) for post in posts_req.json()["data"]]
        except Exception as e:
            flash(f"Error al obtener las publicaciones {e}", "error")

        return render_template(
            "profile.html",
            profile_user=user,
            posts=posts,
            user=current_user(),
        )
    elif request.method == "POST":
        # micro-servicio de usuario
        post_req = requests.post(
            f"{ServicesConfig.USER_SERVICE_URL}/u/{username}",
            headers={"X-User-ID": str(current_user().id)},
            json={"bio": request.form.get("bio", "")},
        )

        if not (post_req.status_code >= 200 and post_req.status_code < 300):
            flash("Error al actualizar el perfil", "error")
        else:
            flash("Perfil actualizado", "success")

        return redirect(url_for("user.profile", username=username))
