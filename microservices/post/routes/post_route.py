from flask import Blueprint, request, abort, jsonify

from db_connector import PostRepository, Post
from dtos import ApiRes

post_api = Blueprint("post", __name__)

# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================


@post_api.route("/post/limit/<int:limit>")
def get_posts_limit(limit: int):
    if limit < 1:
        return ApiRes.error("Limite < 1 no valido").flask_response()
    elif limit > 100:
        return ApiRes.error("Limite > 100 no valido").flask_response()

    title = request.args.get("title", "").strip()
    res = PostRepository.get_posts(limit, title)
    return res.flask_response()


@post_api.route("/post/new", methods=["POST"])
def create_post():
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return ApiRes.unauthorized().flask_response()

    json_data = request.get_json()
    title = json_data.get("title", "").strip()
    content = json_data.get("content", "").strip()
    username = json_data.get("username", "").strip()

    if not title or not content:
        return ApiRes.error("Título y contenido requeridos").flask_response()

    post = Post(
        title=title,
        content=content,
        user_id=user_id,
        username=username,
    )

    res = PostRepository.save(post)
    return res.flask_response()


@post_api.route("/post/<string:post_id>")
def post_detail(post_id: str):
    res = PostRepository.get_by_id(post_id)
    return res.flask_response()


@post_api.route("/post/<string:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id: str):
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return ApiRes.unauthorized().flask_response()

    res = PostRepository.get_by_id(post_id)

    if res.error or not res.success:
        return res.flask_response()

    post = res.data

    if post.user_id != user_id:
        return ApiRes.forbidden().flask_response()

    if request.method == "POST":
        json_data = request.get_json()
        title = json_data.get("title", "").strip()
        content = json_data.get("content", "").strip()

        if not title or not content:
            return ApiRes.error("Título y contenido requeridos").flask_response()

        post.title = title
        post.content = content
        res = PostRepository.save(post)
        return res.flask_response()

    return ApiRes.success("Publicación obtenida", data=post).flask_response()


@post_api.route("/post/<string:post_id>/delete", methods=["POST"])
def delete_post(post_id: str):
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return ApiRes.unauthorized().flask_response()

    res = PostRepository.get_by_id(post_id)

    if res.error or not res.success:
        return res.flask_response()

    post = res.data

    if post.user_id != user_id:
        return ApiRes.forbidden().flask_response()

    res = PostRepository.delete(post_id)
    return res.flask_response()


@post_api.route("/post/user/<string:user_id>", methods=["GET"])
def user_posts(user_id: str):
    res = PostRepository.get_user_posts(user_id)
    return res.flask_response()


@post_api.route("/post/<string:post_id>/exists", methods=["GET"])
def exists_post(post_id: str):
    res = PostRepository.exists(post_id)
    return res.flask_response()
