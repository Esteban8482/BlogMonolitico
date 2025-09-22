"""
Este archivo contiene la configuración de la base de datos y modelos en Firestore.

- Configuración de la base de datos
- consulta simple para comprobar la conexión
"""

import firebase_admin
from firebase_admin import credentials, firestore

from datetime import datetime
from dataclasses import dataclass
from log import logger

FIREBASE_USERS_COLLECTION = "users"

_db = None
_db_user_collection = None


def get_user_collection():
    if _db_user_collection is None:
        raise RuntimeError("Firestore no ha sido inicializado")
    return _db_user_collection


def db_check_user_firestore_connection() -> bool:
    global _db_user_collection

    try:
        _db_user_collection.get()
        return True
    except Exception as e:
        logger.error(f"======== Error al verificar la conexión ========\n{e}\n")
        return False


def db_init_user_firestore(credentials_path):
    global _db, _db_user_collection

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    _db_user_collection = _db.collection(FIREBASE_USERS_COLLECTION)
