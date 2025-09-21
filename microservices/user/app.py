"""
Micro Servicio de Usuarios

- Obtener y actualizar la información de un usuario.
- No renderiza plantillas ni tiene acceso a la base de datos.
- Base de datos independiente de la aplicación.
"""

import sys
import os
from datetime import datetime

from flask import Flask

from db_connector import (
    db_check_user_firestore_connection,
    db_init_user_firestore,
    User,
)
from config import Config
from log import logger


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_override:
        app.config.update(config_override)

    # desde app para mantener actualizada la credencial sin necesidad de reiniciar
    db_init_user_firestore(app.config["FIREBASE_ADMIN_CREDENTIALS"])

    # registrar Blueprints
    from routes import user_api

    app.register_blueprint(user_api)

    return app


app = create_app()


def ensure_db():
    logger.info("Verificando conexión a Firestore...")

    try:
        db_check_user_firestore_connection()
        logger.info("Conexión a Firestore establecida.")
    except Exception as e:
        logger.error("No se pudo conectar a Firestore.")
        logger.error("Error:", e)


if __name__ == "__main__":
    ensure_db()
    app.run(debug=True, port=5002, use_reloader=True)
