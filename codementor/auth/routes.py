"""Registration and session routes."""
import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def safe_next_url(target):
    """Accept only local absolute paths to prevent open redirects."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
            error = "Username must be 3–30 characters using letters, numbers, or underscores."
        elif len(email) > 255 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            error = "Enter a valid email address."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif db.session.scalar(db.select(User).where(or_(func.lower(User.username) == username.lower(), User.email == email))):
            error = "That username or email is already registered."
        if error:
            flash(error, "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Your account is ready. Welcome to CodeMentor AI!", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        user = db.session.scalar(db.select(User).where(or_(func.lower(User.username) == identity.lower(), User.email == identity.lower())))
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=request.form.get("remember") == "on")
            flash("Welcome back!", "success")
            return redirect(safe_next_url(request.args.get("next")) or url_for("dashboard.index"))
        flash("The username/email or password was not recognized.", "danger")
    return render_template("auth/login.html")


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You are signed out.", "info")
    return redirect(url_for("auth.login"))
