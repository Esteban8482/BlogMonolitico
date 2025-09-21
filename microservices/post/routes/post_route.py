from flask import Blueprint, request, abort, jsonify

from db_connector import Post
from services.post_service import (
    create_post as create_post_service,
    get_post,
    update_post,
    delete_post as delete_post_service,
    get_user_posts,
    exists_post as exists_post_service,
    get_posts_service,
)

from log import logger

post_api = Blueprint("post", __name__)

# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================


@post_api.route("/post/limit/<int:limit>")
def get_posts_limit(limit: int):
    if limit < 1:
        return jsonify({"success": False, "message": "Limite no valido"}), 400

    title = request.args.get("title", "").strip()

    try:
        posts = get_posts_service(limit, title)
    except Exception as e:
        logger.error(f"======== Error al obtener las publicaciones ========\n{e}\n")
        return (
            jsonify(
                {"success": False, "message": "Error al obtener las publicaciones"}
            ),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Publicaciones obtenidas",
                "posts": [post.to_json() for post in posts],
            }
        ),
        200,
    )


@post_api.route("/post/new", methods=["POST"])
def create_post():
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    json_data = request.get_json()
    title = json_data.get("title", "").strip()
    content = json_data.get("content", "").strip()
    username = json_data.get("username", "").strip()

    if not title or not content:
        return (
            jsonify({"success": False, "message": "Título y contenido requeridos"}),
            400,
        )

    try:
        post = create_post_service(title, content, user_id, username)
    except Exception as e:
        logger.error(f"======== Error al crear la publicación ========\n{e}\n")
        return (
            jsonify({"success": False, "message": "Error al crear la publicación"}),
            500,
        )

    return (
        jsonify(
            {"success": True, "message": "Publicación creada", "post": post.to_json()}
        ),
        201,
    )


@post_api.route("/post/<string:post_id>")
def post_detail(post_id: str):
    try:
        post = get_post(post_id)
    except Exception as e:
        logger.error(f"======== Error al obtener la publicación ========\n{e}\n")
        return (
            jsonify({"success": False, "message": "Error al obtener la publicación"}),
            500,
        )

    if not post:
        return jsonify({"success": False, "message": "Publicación no encontrada"}), 404

    return (
        jsonify(
            {"success": True, "message": "Publicación obtenida", "post": post.to_json()}
        ),
        200,
    )


@post_api.route("/post/<string:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id: str):
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    try:
        post = get_post(post_id)
    except Exception as e:
        logger.error(f"======== Error al obtener la publicación ========\n{e}\n")
        return (
            jsonify({"success": False, "message": "Error al obtener la publicación"}),
            500,
        )

    if not post:
        return jsonify({"success": False, "message": "Publicación no encontrada"}), 404
    elif post.author.id != user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    if request.method == "POST":
        json_data = request.get_json()
        title = json_data.get("title", "").strip()
        content = json_data.get("content", "").strip()

        if not title or not content:
            return (
                jsonify({"success": False, "message": "Campos requeridos"}),
                400,
            )
        else:
            try:
                post_updated = update_post(post, title, content)
            except Exception as e:
                logger.error(
                    f"======== Error al actualizar la publicación ========\n{e}\n"
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Error al actualizar la publicación",
                            "post": post_updated.to_json(),
                        }
                    ),
                    500,
                )

            return jsonify({"success": True, "message": "Publicación actualizada"}), 200

    return jsonify({"success": True, "post": post.to_json()}), 200


@post_api.route("/post/<string:post_id>/delete", methods=["POST"])
def delete_post(post_id: str):
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    try:
        post = get_post(post_id)
    except Exception as e:
        logger.error(f"======== Error al obtener la publicación ========\n{e}\n")
        return (
            jsonify({"success": False, "message": "Error al obtener la publicación"}),
            500,
        )

    if not post:
        return jsonify({"success": False, "message": "Publicación no encontrada"}), 404
    elif post.author.id != user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    try:
        delete_post_service(post)
    except Exception as e:
        logger.error(f"======== Error al eliminar la publicación ========\n{e}\n")
        return (
            jsonify({"success": False, "message": "Error al eliminar la publicación"}),
            500,
        )

    return jsonify({"success": True, "message": "Publicación eliminada"}), 200


@post_api.route("/post/user/<string:id>", methods=["GET"])
def user_posts(id: str):
    try:
        posts = get_user_posts(id)
    except Exception as e:
        logger.error(f"======== Error al obtener la publicación ========\n{e}\n")
        return (
            jsonify({"success": False, "message": "Error al obtener la publicación"}),
            500,
        )

    return jsonify({"success": True, "posts": [post.to_json() for post in posts]}), 200


@post_api.route("/post/<string:post_id>/exists", methods=["GET"])
def exists_post(post_id: str):
    try:
        exists = exists_post_service(post_id)
    except Exception as e:
        logger.error(
            f"======== Error al verificar si la publicación existe ========\n{e}\n"
        )
        return (
            jsonify({"success": False, "message": "Error al verificar la publicación"}),
            500,
        )

    if not exists:
        return jsonify({"success": False, "message": "Publicación no encontrada"}), 404

    return jsonify({"success": True, "exists": exists}), 200
