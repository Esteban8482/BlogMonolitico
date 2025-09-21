"""
Este archivo contiene la configuración de la base de datos y modelos en Firestore.

- Configuración de la base de datos
- Modelos
    - User para nombre y datos personales como biografía
"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter

from datetime import datetime
from dataclasses import dataclass

FIREBASE_USERS_COLLECTION = "users"

db = None
db_user_collection = None


def db_check_user_firestore_connection():
    return db_user_collection.get()


def db_init_user_firestore(credentials_path=None):
    global db
    global db_user_collection

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    db_user_collection = db.collection(FIREBASE_USERS_COLLECTION)


# =============================
# MODELOS
# =============================
@dataclass
class User:
    """
    No es un modelo soportado por Firestore.
    Sin embargo nos ayuda a modelar la información de un usuario, sin tener que usar JSON manualmente por cada operación.
    """

    id: str
    username: str
    bio: str
    created_at: datetime

    def __repr__(self):
        return f"<User {self.username} {self.id=} {self.created_at=} {self.bio=}>"

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_json(cls, json: dict):
        if json is None:
            return None

        return cls(
            id=json["id"],
            username=json["username"],
            bio=json["bio"],
            created_at=datetime.fromisoformat(json["created_at"]),
        )

    def save_to_db(self):
        db_user_collection.document(str(self.id)).set(self.to_json())

    @staticmethod
    def get_by_username(username: str):
        query_by_username = db_user_collection.where(
            filter=FieldFilter("username", "==", username)
        ).get()
        if query_by_username:
            return User.from_json(query_by_username[0].to_dict())

    @staticmethod
    def get_by_id(user_id: str):
        doc = db_user_collection.document(str(user_id)).get()
        return User.from_json(doc.to_dict())

    @staticmethod
    def get_by_id_or_username(user_id: str, username: str):
        doc_by_id = User.get_by_id(str(user_id))
        if doc_by_id:
            return doc_by_id
        else:
            doc_by_username = User.get_by_username(username)
            return doc_by_username

        return None

    @staticmethod
    def exists_by_username_or_id(user_id: str, username: str):
        doc_by_id = User.get_by_id_or_username(str(user_id), username)
        return doc_by_id is not None
