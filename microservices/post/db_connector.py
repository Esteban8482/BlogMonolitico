"""
Este archivo contiene la configuración de la base de datos y modelos en Firestore.

- Configuración de la base de datos
- Modelos
    - Post para contenido de una publicación
"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter

from datetime import datetime
from dataclasses import dataclass

FIREBASE_POSTS_COLLECTION_collection = "posts"

db = None
db_post_collection = None


def db_check_post_firestore_connection():
    return db_post_collection.get()


def db_init_post_firestore(credentials_path=None):
    global db
    global db_post_collection

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    db_post_collection = db.collection(FIREBASE_POSTS_COLLECTION_collection)


# =============================
# MODELOS
# =============================
@dataclass
class Post:
    """
    No es un modelo soportado por Firestore.
    Sin embargo nos ayuda a modelar la información de un post, sin tener que usar JSON manualmente por cada operación.
    """

    id: str | None
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    username: (
        str  # redundancia de datos pero permite no hacer llamadas a la API de usuario
    )

    def __repr__(self):
        return f"<Post {self.title} {self.id=} {self.created_at=} {self.content=} {self.user_id=}>"

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
            "username": self.username,
        }

    @classmethod
    def from_json(cls, json: dict):
        if json is None:
            return None

        return cls(
            id=json["id"],
            title=json["title"],
            content=json["content"],
            created_at=datetime.fromisoformat(json["created_at"]),
            updated_at=datetime.fromisoformat(json["updated_at"]),
            user_id=json["user_id"],
            username=json["username"],
        )

    def save_to_db(self):
        if self.id:
            db_post_collection.document(str(self.id)).set(self.to_json())
        else:
            doc_ref = db_post_collection.document()
            self.id = doc_ref.id
            doc_ref.set(self.to_json())

    def delete_from_db(self):
        db_post_collection.document(str(self.id)).delete()

    @staticmethod
    def get_by_id(post_id: str):
        doc = db_post_collection.document(str(post_id)).get()
        return Post.from_json(doc.to_dict())

    @staticmethod
    def get_posts(limit: int, title: str = ""):
        if limit < 1:
            return []

        if not title:
            query = db_post_collection.order_by(
                "created_at", direction=firestore.Query.DESCENDING
            ).limit(limit)
        else:
            query = (
                db_post_collection.order_by("title")
                .start_at(title.split(" "))
                .end_at(
                    [t + "\uf8ff" for t in title.split(" ")]
                )  # \uf8ff es el último carácter unicode
                .limit(limit)
            )

        return [Post.from_json(doc.to_dict()) for doc in query.get()]

    @staticmethod
    def get_user_posts(user_id: str):
        query = db_post_collection.where(
            filter=FieldFilter("user_id", "==", user_id)
        ).get()
        return [Post.from_json(doc.to_dict()) for doc in query]

    @staticmethod
    def exists_by_id(post_id: str):
        doc = db_post_collection.document(str(post_id)).get()
        return doc is not None
