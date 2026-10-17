"""CodeMentor AI Flask application factory."""
import click
import os
from flask import Flask

from .config import Config
from .extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object(config_class)
    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401 - registers models with SQLAlchemy
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.context_processor
    def inject_template_helpers():
        from datetime import datetime
        return {"now": datetime.now}

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables for a fresh local install."""
        with app.app_context():
            db.create_all()
        click.echo("Database tables created.")

    return app
