"""Shared Flask extensions, initialized by the application factory."""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to view that page."
login_manager.login_message_category = "info"
csrf = CSRFProtect()
