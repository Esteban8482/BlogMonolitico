from flask import session, flash, redirect, url_for, request
from functools import wraps
from typing import Optional

from db_connector import User

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
            return redirect(url_for("login.login", next=request.path))
        return fn(*args, **kwargs)

    return wrapper
