"""
Este archivo contiene la configuración de la base de datos y modelos en Firestore.

- Configuración de la base de datos
- consulta simple para comprobar la conexión
"""

import firebase_admin
from firebase_admin import credentials, firestore

from log import logger

FIREBASE_POSTS_COLLECTION_collection = "posts"

_db = None
_db_post_collection = None


def get_post_collection():
    if _db_post_collection is None:
        raise RuntimeError("Firestore no ha sido inicializado")
    return _db_post_collection


def db_check_post_firestore_connection() -> bool:
    global _db_post_collection

    try:
        _db_post_collection.get()
        return True
    except Exception as e:
        logger.error(f"======== Error al verificar la conexión ========\n{e}\n")
        return False


def db_init_post_firestore(credentials_path):
    global _db, _db_post_collection

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    _db_post_collection = _db.collection(FIREBASE_POSTS_COLLECTION_collection)
