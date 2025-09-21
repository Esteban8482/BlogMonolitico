"""Aplicación monolítica de Blog con Flask.

Incluye gestión de Usuarios, Publicaciones y Comentarios en una sola base de datos.
Archivo único `main.py` para mantener el enfoque monolítico solicitado.

Este archivo contiene la configuración de la aplicación.
    - Configuración de la base de datos
    - Registro de rutas
    - Inicialización de la base de datos
    - Error handlers
    - Context processors
"""

import sys
import os
from datetime import datetime
import requests

from flask import (
    Flask,
    render_template,
    request,
    flash,
)

from db_connector import db
from helpers import current_user
from config import Config, DB_PATH, ServicesConfig
from dtos import PostDto


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    # registrar Blueprints
    from routes import login_api, post_api, comment_api, user_api

    app.register_blueprint(login_api)
    app.register_blueprint(post_api)
    app.register_blueprint(comment_api)
    app.register_blueprint(user_api)

    # =============================
    # RUTAS PRINCIPALES DEL BLOG
    # =============================

    @app.route("/")
    def index():
        query = request.args.get("q", "").strip()
        post_req = requests.get(
            f"{ServicesConfig.POST_SERVICE_URL}/post/limit/25?title={query}"
        )
        posts = []

        if post_req.status_code >= 200 and post_req.status_code < 300:
            posts = post_req.json()["posts"]
        else:
            try:
                message = post_req.json()["message"]
            except:
                message = "Error al obtener las publicaciones"

            flash(message, "danger")

        try:
            posts = [PostDto.from_json(post) for post in posts]
        except Exception as e:
            flash(f"Error al obtener las publicaciones {e}", "danger")
            posts = []

        return render_template("index.html", posts=posts, user=current_user())

    # =============================
    # COMMAND UTIL / INIT
    # =============================
    @app.cli.command("init-db")
    def init_db_command():  # pragma: no cover - utilidad CLI
        """Inicializa la base de datos."""
        db.create_all()
        print("Base de datos inicializada en", DB_PATH)

    @app.errorhandler(403)
    def forbidden(e):  # pragma: no cover
        return (
            render_template("error.html", code=403, message="No tienes permiso."),
            403,
        )

    @app.errorhandler(404)
    def not_found(e):  # pragma: no cover
        return render_template("error.html", code=404, message="No encontrado."), 404

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user(), "now": datetime.utcnow()}

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
    app.run(debug=True, port=5000, use_reloader=True)
