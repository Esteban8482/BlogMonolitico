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

from db_connector import db
from config import Config, DB_PATH


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    # registrar Blueprints
    from routes import user_api

    app.register_blueprint(user_api)

    # =============================
    # COMMAND UTIL / INIT
    # =============================
    @app.cli.command("init-db")
    def init_db_command():  # pragma: no cover - utilidad CLI
        """Inicializa la base de datos."""
        db.create_all()
        print("Base de datos inicializada en", DB_PATH)

    return app


app = create_app()


def ensure_db():
    print("Verificando base de datos...")

    if not os.path.exists(DB_PATH):
        print("Creando base de datos...")

        with app.app_context():
            db.create_all()
            print("Base de datos creada en", DB_PATH)


if __name__ == "__main__":
    ensure_db()
    app.run(debug=True, port=5002, use_reloader=True)
