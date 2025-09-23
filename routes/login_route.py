from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from firebase_admin import auth as admin_auth
from services.user_service import create_user_profile

login_api = Blueprint("login", __name__)

# =============================
# RUTAS DE AUTENTICACIÓN
# =============================


@login_api.route("/register", methods=["GET"])  # Registro ahora via Firebase UI/JS
def register():
    # Se recomienda registrar la cuenta con Firebase en el frontend.
    # Luego, al iniciar sesión, crearemos el perfil en el microservicio de usuarios.
    return render_template("register.html")


@login_api.route("/login", methods=["GET"])  # Login via Firebase JS (Google/Email)
def login():
    return render_template("login.html")


@login_api.route("/logout")
def logout():
    # Mantener compatibilidad de enlace, pero ahora la sesión real se limpia en /auth/logout (POST)
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("index"))


# Endpoints para sincronizar sesión con Firebase Auth (usados por static/auth.js)
@login_api.route("/auth/session", methods=["POST"])
def auth_session():
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken")
    if not id_token:
        return jsonify({"ok": False, "error": "missing idToken"}), 400
    try:
        decoded = admin_auth.verify_id_token(id_token)
        # Guardamos lo esencial en sesión
        session["user_id"] = decoded.get("uid")
        session["email"] = decoded.get("email")
        # Preferimos displayName; si no, parte local de email como fallback
        display_name = decoded.get("name") or decoded.get("displayName")
        if not display_name:
            email = decoded.get("email") or ""
            display_name = email.split("@")[0] if "@" in email else (decoded.get("uid") or "user")
        session["username"] = display_name

        # Crear perfil de usuario en microservicio si no existe (best-effort)
        try:
            if display_name and decoded.get("uid"):
                create_user_profile(str(decoded["uid"]), str(display_name))
        except Exception:
            pass

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 401


@login_api.route("/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"ok": True})
