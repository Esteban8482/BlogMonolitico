import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = (
        os.environ.get("USER_SECRET_KEY", secrets.token_hex(16)) or "super-secret-key"
    )
    FIREBASE_ADMIN_CREDENTIALS_POSTS = (
        os.environ.get("FIREBASE_ADMIN_CREDENTIALS_POSTS") or "super-secret-key"
    )
