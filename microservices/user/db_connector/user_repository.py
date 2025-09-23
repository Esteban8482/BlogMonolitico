"""
Este archivo contiene los llamados a Firestore.

- Operaciones sobre la base de datos para el microservicio de Usuarios
- Agregar, obtener, actualizar
"""

from google.cloud.firestore_v1 import FieldFilter
from functools import wraps

from .fire_connection import get_user_collection
from .user_model import User
from dtos import ApiRes
from log import logger


def safe_firestore_call(context: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_name = context or func.__name__
                logger.error(
                    f"======== Error en {func_name} file {__file__} ========\n{e}\n"
                )
                return ApiRes.internal_error("Error Interno")

        return wrapper

    return decorator


class UserRepository:
    @staticmethod
    @safe_firestore_call()
    def save(user: User) -> ApiRes:
        try:
            get_user_collection().document(str(user.id)).set(user.to_json())
            doc = get_user_collection().document(str(user.id)).get()

            if not doc.exists:
                return ApiRes.internal_error("Error al guardar el usuario")

            return ApiRes.created("Usuario guardado correctamente")
        except Exception as e:
            return ApiRes.internal_error("Error al guardar el usuario")

    @staticmethod
    @safe_firestore_call()
    def get_by_username(username: str) -> ApiRes[User]:
        query_by_username = (
            get_user_collection()
            .where(filter=FieldFilter("username", "==", username))
            .get()
        )

        if query_by_username:
            user = User.from_json(query_by_username[0].to_dict())
            return ApiRes.success("Usuario encontrado", data=user)
        else:
            return ApiRes.not_found("Usuario no encontrado")

    @staticmethod
    @safe_firestore_call()
    def get_by_id(user_id: str) -> ApiRes[User]:
        doc = get_user_collection().document(str(user_id)).get()

        if not doc.exists:
            return ApiRes.not_found("Usuario no encontrado")

        user = User.from_json(doc.to_dict())
        return ApiRes.success("Usuario encontrado", data=user)

    @staticmethod
    @safe_firestore_call()
    def get_by_id_or_username(user_id: str, username: str) -> ApiRes[User]:
        res = UserRepository.get_by_id(str(user_id))

        if res.success:
            return res

        return UserRepository.get_by_username(username)

    @staticmethod
    @safe_firestore_call()
    def exists_by_username_or_id(user_id: str, username: str) -> ApiRes[bool]:
        res = UserRepository.get_by_id_or_username(str(user_id), username)

        if res.success:
            return ApiRes.success("Usuario encontrado", data=True)

        return ApiRes.not_found("Usuario no encontrado", data=False)
