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
from services.user_service import create_user_profile, exist_user
from helpers import current_user

login_api = Blueprint("login", __name__)

# =============================
# RUTAS DE AUTENTICACIÓN
# =============================


@login_api.route("/register", methods=["GET"])  # Registro ahora via Firebase UI/JS
def register():
    # Se recomienda registrar la cuenta con Firebase en el frontend.
    # Luego, al iniciar sesión, crearemos el perfil en el microservicio de usuarios.
    return render_template("login.html")


@login_api.route("/login", methods=["GET"])  # Login via Firebase JS (Google/Email)
def login():
    if current_user():
        return redirect(url_for("index"))

    return render_template("login.html")


# Endpoints para sincronizar sesión con Firebase Auth (usados por static/auth.js)
@login_api.route("/auth/session", methods=["POST"])
def auth_session():
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"ok": False, "error": "missing idToken"}), 400

    try:
        # desfasar la respuesta para que firebase no marque el token como usado muy reciente
        decoded = admin_auth.verify_id_token(id_token, clock_skew_seconds=10)

        # Preferimos displayName; si no, parte local de email como fallback
        display_name = decoded.get("name") or decoded.get("displayName")
    except Exception as e:
        print("==================== ERROR", e)
        flash("Error al iniciar sesión", "danger")
        return jsonify({"ok": False, "redirect": url_for("login.login")}), 400

    if not display_name:
        email = decoded.get("email") or ""
        display_name = (
            email.split("@")[0] if "@" in email else (decoded.get("uid") or "user")
        )

    # Guardamos lo esencial en sesión
    session["user_id"] = decoded.get("uid")
    session["email"] = decoded.get("email")
    session["username"] = display_name

    # microservicio de usuarios, si existe evitar agregarlo y redirigir
    if exist_user(decoded["uid"], display_name):
        return jsonify({"ok": True, "redirect": url_for("index")})
    elif not (display_name and decoded.get("uid")):
        session.clear()
        flash("Error al crear perfil de usuario o iniciar sesión", "danger")
        return jsonify({"ok": False, "redirect": url_for("login.login")}), 400

    # Crear perfil de usuario en microservicio si no existe (best-effort)
    user = create_user_profile(str(decoded["uid"]), str(display_name))

    if not user:
        session.clear()
        flash("Error al crear perfil de usuario o iniciar sesión", "danger")
        return jsonify({"ok": False, "redirect": url_for("login.login")}), 500

    return jsonify({"ok": True, "redirect": url_for("index")})


@login_api.route("/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"ok": True})
