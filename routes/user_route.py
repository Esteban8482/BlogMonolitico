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
            user = UserDto.from_json(user_req.json()["profile_user"])
        except Exception as e:
            flash("Error al obtener el perfil", "error")
            abort(404)

        posts_req = requests.get(
            f"{ServicesConfig.POST_SERVICE_URL}/post/user/{user.id}",
            headers={"X-User-ID": str(current_user().id)},
        )

        if posts_req.status_code != 200:
            flash("Error al obtener las publicaciones", "error")
            abort(404)

        posts = []

        try:
            posts = [PostDto.from_json(post) for post in posts_req.json()["posts"]]
        except Exception as e:
            print(e)
            flash("Error al obtener las publicaciones", "error")

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

        if post_req.status_code == 200:
            flash("Perfil actualizado", "success")
        else:
            flash("Error al actualizar el perfil", "error")

        return redirect(url_for("user.profile", username=username))
