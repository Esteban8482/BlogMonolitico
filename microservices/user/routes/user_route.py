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

user_api = Blueprint("user", __name__)

# =============================
# PERFIL DE USUARIO
# =============================


@user_api.route("/u/<username>", methods=["GET", "POST"])
def profile(username: str):
    print(f"======== Obteniendo perfil {username} ========")

    user_id = request.headers.get("X-User-ID")

    print(f"======== id {user_id} ========")
    print(f"======== username {username} ========")

    if not user_id:
        abort(403)

    user = get_user_or_404(username)

    print(f"======== user {user} ========")

    if request.method == "POST":
        data = request.get_json()
        print(f"======== profile POST {data} ========")

        if user.id != int(user_id):
            abort(403)

        bio = data.get("bio", "")
        update_user_bio(user, bio)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Perfil actualizado",
                    "profile_user": user.to_json(),
                }
            ),
            200,
        )

    return jsonify({"success": True, "profile_user": user.to_json()}), 200


@user_api.route("/u/new", methods=["POST"])
def register_user():
    data = UserReqDto.from_json(request.get_json())

    if exists_user(data.id, data.username):
        return jsonify({"success": False, "message": "El usuario ya existe"}), 409

    print(f"======== Creando usuario {data} ========")
    user = create_user(data.id, data.username)

    if not user:
        return jsonify({"success": False, "message": "Error al crear el usuario"}), 500

    print(f"======== Usuario creado {user} ========")

    return jsonify({"success": True, "message": "Usuario creado"}), 200
