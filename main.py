"""Aplicación monolítica de Blog con Flask.

Incluye gestión de Usuarios, Publicaciones y Comentarios en una sola base de datos.
Archivo único `main.py` para mantener el enfoque monolítico solicitado.
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime
from functools import wraps
from typing import Optional

from flask import (
	Flask,
	render_template,
	request,
	redirect,
	url_for,
	flash,
	session,
	abort,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "blog.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("BLOG_SECRET_KEY", secrets.token_hex(16))

db = SQLAlchemy(app)


# =============================
# MODELOS
# =============================
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	bio = db.Column(db.Text, default="")

	posts = db.relationship("Post", backref="author", lazy=True, cascade="all, delete-orphan")
	comments = db.relationship("Comment", backref="author", lazy=True, cascade="all, delete-orphan")

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	content = db.Column(db.Text, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

	comments = db.relationship("Comment", backref="post", lazy=True, cascade="all, delete-orphan")


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
	post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False, index=True)


# =============================
# UTILS / AUTH HELPERS
# =============================
def current_user() -> Optional[User]:
	uid = session.get("user_id")
	if uid is None:
		return None
	return User.query.get(uid)


def login_required(fn):
	@wraps(fn)
	def wrapper(*args, **kwargs):
		if not current_user():
			flash("Debes iniciar sesión.", "warning")
			return redirect(url_for("login", next=request.path))
		return fn(*args, **kwargs)

	return wrapper


# =============================
# RUTAS DE AUTENTICACIÓN
# =============================
@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		confirm = request.form.get("confirm", "")
		if not username or not email or not password:
			flash("Completa todos los campos", "danger")
		elif password != confirm:
			flash("Las contraseñas no coinciden", "danger")
		elif User.query.filter((User.username == username) | (User.email == email)).first():
			flash("Usuario o correo ya existe", "danger")
		else:
			user = User(username=username, email=email)
			user.set_password(password)
			db.session.add(user)
			db.session.commit()
			flash("Registro exitoso. Inicia sesión.", "success")
			return redirect(url_for("login"))
	return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username_or_email = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		user = User.query.filter(
			(User.username == username_or_email) | (User.email == username_or_email.lower())
		).first()
		if not user or not user.check_password(password):
			flash("Credenciales inválidas", "danger")
		else:
			session["user_id"] = user.id
			flash("Bienvenido de nuevo", "success")
			next_url = request.args.get("next")
			return redirect(next_url or url_for("index"))
	return render_template("login.html")


@app.route("/logout")
def logout():
	session.pop("user_id", None)
	flash("Sesión cerrada", "info")
	return redirect(url_for("index"))


# =============================
# RUTAS PRINCIPALES DE POSTS
# =============================
@app.route("/")
def index():
	q = request.args.get("q", "").strip()
	query = Post.query.order_by(Post.created_at.desc())
	if q:
		like = f"%{q}%"
		query = query.filter((Post.title.ilike(like)) | (Post.content.ilike(like)))
	posts = query.limit(25).all()
	return render_template("index.html", posts=posts, q=q, user=current_user())


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		if not title or not content:
			flash("Título y contenido requeridos", "danger")
		else:
			post = Post(title=title, content=content, author=current_user())
			db.session.add(post)
			db.session.commit()
			flash("Publicación creada", "success")
			return redirect(url_for("post_detail", post_id=post.id))
	return render_template("create_post.html")


def _require_post_owner(post: Post):
	if not current_user() or post.author.id != current_user().id:
		abort(403)


@app.route("/post/<int:post_id>")
def post_detail(post_id: int):
	post = Post.query.get_or_404(post_id)
	return render_template("post_detail.html", post=post, user=current_user())


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
	post = Post.query.get_or_404(post_id)
	_require_post_owner(post)
	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		if not title or not content:
			flash("Campos requeridos", "danger")
		else:
			post.title = title
			post.content = content
			db.session.commit()
			flash("Publicación actualizada", "success")
			return redirect(url_for("post_detail", post_id=post.id))
	return render_template("edit_post.html", post=post)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
	post = Post.query.get_or_404(post_id)
	_require_post_owner(post)
	db.session.delete(post)
	db.session.commit()
	flash("Publicación eliminada", "info")
	return redirect(url_for("index"))


# =============================
# RUTAS DE COMENTARIOS
# =============================
@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id: int):
	post = Post.query.get_or_404(post_id)
	content = request.form.get("content", "").strip()
	if not content:
		flash("Comentario vacío", "danger")
	else:
		comment = Comment(content=content, author=current_user(), post=post)
		db.session.add(comment)
		db.session.commit()
		flash("Comentario agregado", "success")
	return redirect(url_for("post_detail", post_id=post.id))


@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id: int):
	comment = Comment.query.get_or_404(comment_id)
	if comment.author.id != current_user().id and comment.post.author.id != current_user().id:
		abort(403)
	post_id = comment.post.id
	db.session.delete(comment)
	db.session.commit()
	flash("Comentario eliminado", "info")
	return redirect(url_for("post_detail", post_id=post_id))


# =============================
# PERFIL DE USUARIO
# =============================
@app.route("/u/<username>", methods=["GET", "POST"])
def profile(username: str):
	user = User.query.filter_by(username=username).first_or_404()
	if request.method == "POST":
		if not current_user() or current_user().id != user.id:
			abort(403)
		bio = request.form.get("bio", "")
		user.bio = bio
		db.session.commit()
		flash("Perfil actualizado", "success")
		return redirect(url_for("profile", username=user.username))
	posts = Post.query.filter_by(author=user).order_by(Post.created_at.desc()).all()
	return render_template("profile.html", profile_user=user, posts=posts, user=current_user())


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
	app.run(debug=True, port=5000)

