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

from db_connector import db_check_user_firestore_connection, db_init_user_firestore
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
        db_init_user_firestore(app.config["FIREBASE_ADMIN_CREDENTIALS"])

    # registrar Blueprints
    from routes import user_api

    app.register_blueprint(user_api)

    return app


def ensure_db():
    logger.info("Verificando conexión a Firestore...")
    success = db_check_user_firestore_connection()

    if success:
        logger.info("Conexión a Firestore establecida.")
    else:
        logger.error("No se pudo conectar a Firestore.")


if __name__ == "__main__":
    app = create_app()
    ensure_db()
    app.run(debug=True, port=5002, use_reloader=True)
