from flask import session, flash, redirect, url_for, request
from functools import wraps
from typing import Optional

<<<<<<< HEAD
from db_connector import User, db
=======
from db_connector import User
>>>>>>> main

# =============================
# UTILS / AUTH HELPERS
# =============================


def current_user() -> Optional[User]:
    uid = session.get("user_id")
<<<<<<< HEAD

    if uid is None:
        return None

    return db.session.get(User, uid)
=======
    uname = session.get("username")
    email = session.get("email")

    if not uid or not uname:
        return None

    return User(id=str(uid), username=str(uname), email=email)
>>>>>>> main


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("login.login", next=request.path))
        return fn(*args, **kwargs)

    return wrapper
