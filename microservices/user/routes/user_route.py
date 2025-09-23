from flask import (
    Blueprint,
    request,
    abort,
    jsonify,
)

from db_connector import UserRepository, User
from dtos import UserReqDto, ApiRes
from log import logger

user_api = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_api.route("/u/<username>", methods=["GET", "POST"])
def profile(username: str):
    user_id = request.headers.get("X-User-ID")

    logger.info(f"======== Obteniendo perfil ========\n{username=} {user_id=}\n")

    if not user_id:
        return ApiRes.unauthorized().flask_response()

    res = UserRepository.get_by_username(username)

    if not res:
        return res.flask_response()

    user = res.data
    logger.info(f"======== user {user} ========")

    if request.method == "POST":
        data = request.get_json()
        logger.info(f"======== profile POST ========\n{data=}\n")

        if str(user.id) != str(user_id):
            return ApiRes.forbidden().flask_response()

        bio = data.get("bio", "")
        user.bio = bio
        res = UserRepository.save(user)
        return res.flask_response()

    return ApiRes.success("Perfil obtenido", data=user).flask_response()


@user_api.route("/u/new", methods=["POST"])
def register_user():
    try:
        data = UserReqDto.from_json(request.get_json())
        logger.info(f"======== profile POST ========\n{data=}\n")
    except Exception as e:
        logger.error(f"======== Error al obtener datos del request ========\n{e}\n")
        return ApiRes.error(
            "Completa todos los campos necesarios (id, username)"
        ).flask_response()

    res = UserRepository.exists_by_username_or_id(data.id, data.username)

    if res.error:
        return res.flask_response()
    elif res.data:
        return ApiRes.conflict("El usuario ya existe").flask_response()

    logger.info(f"======== Creando usuario ========\n{data=}\n")

    user = User(id=data.id, username=data.username)
    res = UserRepository.save(user)

    if not res:
        return res.flask_response()

    logger.info(f"======== Usuario creado ========\n{user=}\n")
    return ApiRes.success("Usuario creado", data=user).flask_response()
