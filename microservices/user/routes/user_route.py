from flask import (
    Blueprint,
    request,
    abort,
    jsonify,
)
from services.user_service import (
    get_user_or_404,
    update_user_bio,
    exists_user,
    create_user,
)

from dtos import UserReqDto
from log import logger

user_api = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_api.route("/u/<username>", methods=["GET", "POST"])
def profile(username: str):
    logger.info(f"======== Obteniendo perfil {username} ========")

    user_id = request.headers.get("X-User-ID")
    logger.info(f"======== id req {user_id} ========")

    if not user_id:
        abort(403)

    user = get_user_or_404(username)

    if not user:
        abort(404)

    logger.info(f"======== user {user} ========")

    if request.method == "POST":
        data = request.get_json()
        logger.info(f"======== profile POST {data} ========")

        if user.id != int(user_id):
            abort(403)

        bio = data.get("bio", "")
        user_updated = update_user_bio(user, bio)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Perfil actualizado",
                    "profile_user": user_updated.to_json(),
                }
            ),
            200,
        )

    return jsonify({"success": True, "profile_user": user.to_json()}), 200


@user_api.route("/u/new", methods=["POST"])
def register_user():
    try:
        data = UserReqDto.from_json(request.get_json())
        logger.info(f"======== profile POST {data} ========")
    except Exception as e:
        logger.error(f"======== Error al obtener datos del request ========\n{e}\n")
        return jsonify({"success": False, "message": "Completa todos los campos"}), 400

    try:
        if exists_user(data.id, data.username):
            return jsonify({"success": False, "message": "El usuario ya existe"}), 409
    except Exception as e:
        logger.error(
            f"======== Error al verificar si el usuario existe ========\n{e}\n"
        )
        return (
            jsonify({"success": False, "message": "Error al verificar el usuario"}),
            500,
        )

    logger.info(f"======== Creando usuario {data} ========")

    try:
        user = create_user(data.id, data.username)
    except Exception as e:
        logger.error(f"======== Error al crear el usuario ========\n{e}\n")
        return jsonify({"success": False, "message": "Error al crear el usuario"}), 500

    if not user:
        return jsonify({"success": False, "message": "Error al crear el usuario"}), 500

    logger.info(f"======== Usuario creado {user} ========")

    return jsonify({"success": True, "message": "Usuario creado"}), 200
