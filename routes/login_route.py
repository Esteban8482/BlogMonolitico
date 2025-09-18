from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connector import User
from db_connector import db

login_route = Blueprint("login", __name__)

# =============================
# RUTAS DE AUTENTICACIÓN
# =============================


@login_route.route("/register", methods=["GET", "POST"])
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
        elif User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            flash("Usuario o correo ya existe", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for("login.login"))
    return render_template("register.html")


@login_route.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter(
            (User.username == username_or_email)
            | (User.email == username_or_email.lower())
        ).first()
        if not user or not user.check_password(password):
            flash("Credenciales inválidas", "danger")
        else:
            session["user_id"] = user.id
            flash("Bienvenido de nuevo", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("index"))
    return render_template("login.html")


@login_route.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Sesión cerrada", "info")
    return redirect(url_for("index"))
