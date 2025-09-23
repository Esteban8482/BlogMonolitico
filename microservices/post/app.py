"""
Micro Servicio de Post

- Crear post
- Obtener post por ID
- Actualizar post
- Eliminar post
- Obtener posts de un usuario

- Conexión a Firestore para almacenar los posts
"""

import sys
import os
from datetime import datetime

from flask import Flask

from db_connector import db_check_post_firestore_connection, db_init_post_firestore
from config import Config
from log import logger
from dotenv import load_dotenv
load_dotenv()


def create_app(config_override=None, init_db=True):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_override:
        app.config.update(config_override)

    if init_db:
        # desde app para mantener actualizada la credencial sin necesidad de reiniciar
        db_init_post_firestore(app.config["FIREBASE_ADMIN_CREDENTIALS_POSTS"])

    # registrar Blueprints
    from routes import post_api

    app.register_blueprint(post_api)

    return app


def ensure_db():
    logger.info("Verificando conexión a Firestore...")

    try:
        db_check_post_firestore_connection()
        logger.info("Conexión a Firestore establecida.")
    except Exception as e:
        logger.error("No se pudo conectar a Firestore.")
        logger.error("Error:", e)


if __name__ == "__main__":
    app = create_app()
    ensure_db()
    app.run(debug=True, port=5003, use_reloader=True)
