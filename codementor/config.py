"""Environment-backed application settings."""
import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "local-development-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{Path(__file__).resolve().parent.parent / 'instance' / 'codementor.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = 3600
