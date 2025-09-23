"""Aplicación monolítica de Blog con Flask.

Migrada para usar Firebase Authentication en lugar de una base de datos local
para autenticación. Este archivo contiene la configuración de la aplicación.
    - Registro de rutas
    - Inicialización de Firebase Admin (Auth)
    - Error handlers
    - Context processors
"""

import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    flash,
)

import firebase_admin
from firebase_admin import credentials
from helpers import current_user
from config import Config
from services.post_service import get_post_limit


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_override:
        app.config.update(config_override)

    # Inicializar Firebase Admin si aún no está inicializado
    try:
        if not firebase_admin._apps:
            cred_path = app.config.get("FIREBASE_ADMIN_CREDENTIALS")

            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Intento con variables de entorno (GOOGLE_APPLICATION_CREDENTIALS)
                firebase_admin.initialize_app()
    except Exception as e:
        # No detenemos la app si falla; los endpoints de sesión reportarán el error
        app.logger.error(f"Firebase Admin init failed: {e}")

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
        posts = get_post_limit(25, query)

        if posts is None:
            flash(f"Error al obtener las publicaciones", "danger")
            posts = []

        return render_template("index.html", posts=posts, user=current_user())

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
        # Config opcional para Firebase Frontend (puede provenir de env)
        fb_cfg = {
            "apiKey": os.environ.get("FIREBASE_API_KEY"),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.environ.get("FIREBASE_APP_ID"),
            "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),
        }

        # El template decide si sobreescribe defaults; si están vacíos, se ignoran
        return {
            "current_user": current_user(),
            "now": datetime.now(),
            "firebase_config": fb_cfg,
        }

    @app.after_request
    def remove_coop_headers(response):
        if request.path == "/login":  # o la ruta que renderiza tu template
            response.headers.pop("Cross-Origin-Opener-Policy", None)
            response.headers.pop("Cross-Origin-Embedder-Policy", None)
        return response
    
    @app.get("/health")
    def heatlh():
        return {"status": "ok"}
    
    @app.get("/live")
    def live():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    # Bind to 0.0.0.0 for Docker container networking
    app.run(host="0.0.0.0", debug=True, port=5000, use_reloader=True)
