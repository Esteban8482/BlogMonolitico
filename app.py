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
import secrets
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
)

from db_connector import db, Post
from helpers import current_user


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "blog.db")

sys.path.append(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get(
        "BLOG_SECRET_KEY", secrets.token_hex(16))

    db.init_app(app)

    # registrar Blueprints
    from routes import login_route, post_route, comment_route, user_route
    app.register_blueprint(login_route)
    app.register_blueprint(post_route)
    app.register_blueprint(comment_route)
    app.register_blueprint(user_route)

    return app


app = create_app()


# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    query = Post.query.order_by(Post.created_at.desc())
    if q:
        like = f"%{q}%"
        query = query.filter((Post.title.ilike(like)) |
                             (Post.content.ilike(like)))
    posts = query.limit(25).all()
    return render_template("index.html", posts=posts, q=q, user=current_user())


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
    return render_template("error.html", code=403, message="No tienes permiso."), 403


@app.errorhandler(404)
def not_found(e):  # pragma: no cover
    return render_template("error.html", code=404, message="No encontrado."), 404


@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "now": datetime.utcnow()}


def ensure_db():
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()


if __name__ == "__main__":
    ensure_db()
    app.run(debug=True, port=5000, use_reloader=True)
