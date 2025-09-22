"""Aplicación monolítica de Blog con Flask.

Incluye gestión de Usuarios, Publicaciones y Comentarios en una sola base de datos.
Archivo único `main.py` para mantener el enfoque monolítico solicitado.
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime
from functools import wraps
from typing import Optional, Tuple, Dict, Any
import json

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

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, auth as fb_auth


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "blog.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("BLOG_SECRET_KEY", secrets.token_hex(16))

db = SQLAlchemy(app)


# =============================
# FIREBASE ADMIN INIT
# =============================
def init_firebase_admin() -> None:
	"""Inicializa Firebase Admin con credenciales del entorno.

	Busca credenciales de dos maneras:
	- Ruta a JSON de servicio en FIREBASE_CREDENTIALS_JSON
	- JSON embebido en FIREBASE_CREDENTIALS (contenido del archivo)
	"""
	if firebase_admin._apps:  # ya inicializado
		return
	cred: Optional[credentials.Base] = None
	json_path = os.environ.get("FIREBASE_CREDENTIALS_JSON")
	json_inline = os.environ.get("FIREBASE_CREDENTIALS")
	if json_path and os.path.exists(json_path):
		cred = credentials.Certificate(json_path)
	elif json_inline:
		try:
			sa_dict = json.loads(json_inline)
			cred = credentials.Certificate(sa_dict)
		except Exception:
			cred = None
	else:
		# Fallback a credencial por aplicación (para entorno con GOOGLE_APPLICATION_CREDENTIALS)
		try:
			cred = credentials.ApplicationDefault()
		except Exception:
			cred = None
	if cred is None:
		# Dejar sin inicializar; endpoints que lo requieran responderán 503
		return
	firebase_admin.initialize_app(cred)


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


def verify_firebase_token(id_token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
	"""Verifica un ID token de Firebase y retorna los claims o un error."""
	if not firebase_admin._apps:
		init_firebase_admin()
	if not firebase_admin._apps:
		return None, "Firebase Admin no inicializado"
	try:
		decoded = fb_auth.verify_id_token(id_token)
		return decoded, None
	except Exception as e:  # noqa: BLE001
		return None, str(e)


def _extract_id_token_from_request() -> Optional[str]:
	# Authorization: Bearer <token>
	auth_header = request.headers.get("Authorization", "")
	if auth_header.startswith("Bearer "):
		return auth_header.split(" ", 1)[1].strip()
	# Campo oculto en formularios
	if request.method in {"POST", "PUT", "PATCH"}:
		token = request.form.get("__firebase_id_token")
		if token:
			return token
		data = request.get_json(silent=True) or {}
		if isinstance(data, dict) and data.get("idToken"):
			return data.get("idToken")
	return None


@app.before_request
def ensure_session_from_firebase_token():
	"""Si no hay sesión local, intenta derivarla de un ID token de Firebase."""
	if session.get("user_id"):
		return  # ya existe sesión
	token = _extract_id_token_from_request()
	if not token:
		return
	claims, err = verify_firebase_token(token)
	if err or not claims:
		return
	email = claims.get("email")
	if not email:
		return
	user = User.query.filter((User.email == email) | (User.username == email)).first()
	if not user:
		user = User(username=email, email=email, password_hash=generate_password_hash(secrets.token_hex(16)))
		db.session.add(user)
		db.session.commit()
	session["user_id"] = user.id


@app.before_request
def require_login_everywhere():
	"""Enforce login for all pages except auth/static endpoints and login page.

	Esto evita que se vean páginas sin autenticación incluso si el JS del cliente no corre.
	"""
	# Permitir métodos preflight
	if request.method == "OPTIONS":
		return

	# Usar nombre del endpoint para determinar si es público
	public_endpoints = {
		# Páginas públicas
		"index",
		"post_detail",
		"profile",
		# Autenticación/registro
		"login",
		"register",
		"logout",  # permitir acceder incluso sin sesión para evitar bucles
		# Endpoints AJAX de auth
		"auth_session",
		"auth_logout",
		# Archivos estáticos
		"static",
	}

	endpoint = request.endpoint  # puede ser None en algunos 404
	path = request.path or "/"
	if endpoint in public_endpoints or path == "/favicon.ico" or (path.startswith("/auth/") or path.startswith("/static/")):
		return

	# Si ya hay sesión, dejar pasar
	if session.get("user_id"):
		return

	# Redirigir a login con next
	next_url = request.url
	return redirect(url_for("login", next=next_url))


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
	# Si ya hay sesión de servidor, evitar mostrar el login otra vez
	if request.method == "GET" and session.get("user_id"):
		next_url = request.args.get("next")
		return redirect(next_url or url_for("index"))
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
# ENDPOINTS DE SESIÓN (FIREBASE)
# =============================
@app.route("/auth/session", methods=["POST"])  # AJAX: sin recarga
def auth_session():
	"""Sincroniza la sesión de servidor con un ID token de Firebase.

	Espera JSON: { idToken: string }
	- Verifica token
	- Busca/crea usuario local por uid/email
	- Guarda session.user_id
	Retorna 200/401/503 con JSON.
	"""
	data = request.get_json(silent=True) or {}
	id_token = data.get("idToken", "")
	if not id_token:
		return {"ok": False, "error": "Falta idToken"}, 400
	claims, err = verify_firebase_token(id_token)
	if err:
		return {"ok": False, "error": f"Token inválido: {err}"}, 401
	email = claims.get("email")
	uid = claims.get("uid")
	if not email or not uid:
		return {"ok": False, "error": "Token sin email/uid"}, 401
	user = User.query.filter((User.email == email) | (User.username == email)).first()
	if not user:
		# Crear usuario local con email como username por defecto (conservador)
		user = User(username=email, email=email, password_hash=generate_password_hash(secrets.token_hex(16)))
		db.session.add(user)
		db.session.commit()
	session["user_id"] = user.id
	return {"ok": True, "userId": user.id}


@app.route("/auth/logout", methods=["POST"])  # AJAX
def auth_logout():
	session.pop("user_id", None)
	return {"ok": True}


@app.route("/me")
@login_required
def me():
	u = current_user()
	return redirect(url_for("profile", username=u.username))


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
	# Exponer config de Firebase para el template de layout
	firebase_config = {
		"apiKey": os.environ.get("FIREBASE_API_KEY", ""),
		"authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
		"projectId": os.environ.get("FIREBASE_PROJECT_ID", ""),
		"storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
		"messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
		"appId": os.environ.get("FIREBASE_APP_ID", ""),
		"measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID", ""),
	}
	return {"current_user": current_user(), "now": datetime.utcnow(), "firebase_config": firebase_config}


def ensure_db():
	if not os.path.exists(DB_PATH):
		with app.app_context():
			db.create_all()


if __name__ == "__main__":
	ensure_db()
	init_firebase_admin()
	app.run(debug=True, port=5000)

