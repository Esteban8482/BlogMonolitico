from typing import List

"""
Este archivo contiene los llamados a Firestore.

- Operaciones sobre la base de datos para el microservicio de Usuarios
- Agregar, obtener, actualizar
"""

from google.cloud.firestore_v1 import FieldFilter
from firebase_admin import firestore
from functools import wraps

from .fire_connection import get_post_collection
from .post_model import Post
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


class PostRepository:
    @staticmethod
    @safe_firestore_call()
    def save(post: Post) -> ApiRes[Post]:
        collection = get_post_collection()

        if post.id:
            doc_ref = collection.document(str(post.id))
            doc = doc_ref.get()

            if not doc.exists:
                return ApiRes.not_found("El post no existe para editar")

            doc_ref.set(post.to_json())
            return ApiRes.success("Post actualizado correctamente", data=post)

        doc_ref = collection.document()
        post.id = doc_ref.id
        doc_ref.set(post.to_json())
        post = Post.from_json(doc_ref.get().to_dict())
        return ApiRes.created("Post creado correctamente", data=post)

    @staticmethod
    @safe_firestore_call()
    def delete(post_id: str) -> ApiRes:
        doc_ref = get_post_collection().document(str(post_id))
        doc = doc_ref.get()

        if not doc.exists:
            return ApiRes.not_found("El post no existe")

        doc_ref.delete()
        return ApiRes.success("Post eliminado correctamente")

    @staticmethod
    @safe_firestore_call()
    def get_by_id(post_id: str) -> ApiRes[Post]:
        doc = get_post_collection().document(str(post_id)).get()

        if not doc.exists:
            return ApiRes.not_found("El post no existe")

        return ApiRes.success(
            "Post encontrado",
            data=Post.from_json(doc.to_dict()),
        )

    @staticmethod
    @safe_firestore_call()
    def exists(post_id: str) -> ApiRes[bool]:
        res = PostRepository.get_by_id(post_id)

        if res.success:
            return ApiRes.success("Post encontrado", data=True)

        return ApiRes.not_found("Post no encontrado", data=False)

    @staticmethod
    @safe_firestore_call()
    def get_posts(limit: int, title: str = "") -> ApiRes[List[Post]]:
        if limit < 1:
            return ApiRes.error("El limite debe ser mayor a 0")

        if not title:
            query = (
                get_post_collection()
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
        else:
            query = (
                get_post_collection()
                .order_by("title")
                .start_at(title.split(" "))
                .end_at(
                    [t + "\uf8ff" for t in title.split(" ")]
                )  # \uf8ff es el último carácter unicode
                .limit(limit)
            )

        posts = [Post.from_json(doc.to_dict()) for doc in query.get()]
        return ApiRes.success("Posts obtenidas", data=posts)

    @staticmethod
    @safe_firestore_call()
    def get_user_posts(user_id: str) -> ApiRes[List[Post]]:
        query = (
            get_post_collection()
            .where(filter=FieldFilter("user_id", "==", user_id))
            .get()
        )
        print("=================", query)
        posts = [Post.from_json(doc.to_dict()) for doc in query]
        return ApiRes.success("Posts obtenidas", data=posts)
