from google.cloud import firestore
from google.oauth2 import service_account
import os

_db = None


def get_db():
    global _db
    if _db is None:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        credentials = service_account.Credentials.from_service_account_file(cred_path)
        _db = firestore.Client(credentials=credentials)
    return _db
