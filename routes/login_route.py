from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import register_user, authenticate_user
import requests
from config import ServicesConfig

login_api = Blueprint("login", __name__)

# =============================
# RUTAS DE AUTENTICACIÓN
# =============================


@login_api.route("/register", methods=["GET", "POST"])
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
        else:
            reg_user = register_user(username, email, password)

            if not reg_user:
                flash(
                    "Usuario o correo ya existe o error al crear el usuario", "danger"
                )
                return redirect(url_for("login.register"))

            # registrar usuarios en el microservicio de usuario
            user_req = requests.post(
                f"{ServicesConfig.USER_SERVICE_URL}/u/new",
                json={"id": reg_user.id, "username": username},
            )

            if user_req.status_code != 200:
                flash("Error al crear el usuario", "danger")
                return redirect(url_for("login.register"))

            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for("login.login"))

    return render_template("register.html")


@login_api.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = authenticate_user(username_or_email, password)

        if not user:
            flash("Credenciales inválidas", "danger")
        else:
            session["user_id"] = user.id
            flash("Bienvenido de nuevo", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("index"))

    return render_template("login.html")


@login_api.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Sesión cerrada", "info")
    return redirect(url_for("index"))
