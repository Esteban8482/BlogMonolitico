from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
import requests

from services.comment_service import get_post_comments
from helpers import current_user, login_required
from config import ServicesConfig
from dtos import PostDto


post_api = Blueprint("post", __name__)

# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================


@post_api.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post_rq = requests.post(
            f"{ServicesConfig.POST_SERVICE_URL}/post/new",
            headers={"X-User-ID": str(current_user().id)},
            json={
                "title": request.form.get("title", "").strip(),
                "content": request.form.get("content", "").strip(),
            },
        )

        if post_rq.status_code >= 200 and post_rq.status_code < 300:
            message = post_rq.json()["message"] if "message" in post_rq.json() else ""
            flash(message, "success")

            post = PostDto.from_json(post_rq.json()["post"])
            return redirect(url_for("post.post_detail", post_id=post.id))
        else:
            try:
                message = (
                    post_rq.json()["message"] if "message" in post_rq.json() else ""
                )
                flash(message, "danger")
            except:
                flash("Error al crear la publicación", "danger")

            return redirect(url_for("post.create_post"))

    return render_template("create_post.html")


@post_api.route("/post/<string:post_id>")
@login_required
def post_detail(post_id: str):
    print(f"\n\n========={post_id=}=========\n\n")

    post_req = requests.get(
        f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}",
        headers={"X-User-ID": str(current_user().id)},
    )

    if not (post_req.status_code >= 200 and post_req.status_code < 300):
        try:
            message = post_req.json()["message"]
        except:
            message = "Error al obtener la publicación"

        flash(message, "danger")
        abort(404)

    try:
        post = PostDto.from_json(post_req.json()["post"])
    except:
        flash("Error al obtener la publicación", "danger"), abort(500)
        flash("Error al obtener la publicación", "danger")
        abort(404)

    comments = []

    try:
        comments = get_post_comments(post.id)
    except:
        flash("Error al obtener los comentarios", "danger")

    return render_template(
        "post_detail.html", post=post, user=current_user(), comments=comments
    )


@post_api.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    if request.method == "GET":
        post_req = requests.get(
            f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}/edit",
            headers={"X-User-ID": str(current_user().id)},
        )

        return render_template("edit_post.html", post=post)
    elif request.method == "POST":
        post_req = requests.post(
            f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}/edit",
            headers={"X-User-ID": str(current_user().id)},
            json={
                "title": request.form.get("title", "").strip(),
                "content": request.form.get("content", "").strip(),
            },
        )

        if post_req.status_code != 200:
            flash(post_req.json()["message"], "danger")
            return redirect(url_for("post.edit_post", post_id=post_id))
        else:
            flash(post_req.json()["message"], "success")

            post = PostDto.from_json(post_req.json()["post"])
            return redirect(url_for("post.post_detail", post_id=post.id))


@post_api.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post_eq = get_post_or_404(post_id)

    post_req = requests.post(
        f"{ServicesConfig.POST_SERVICE_URL}/post/{post_id}/delete",
        headers={"X-User-ID": str(current_user().id)},
    )

    if post_req.status_code != 200:
        flash(post_req.json()["message"], "danger")
        return redirect(url_for("post.post_detail", post_id=post_id))

    flash(post_req.json()["message"], "success")
    return redirect(url_for("index"))
