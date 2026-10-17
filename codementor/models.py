"""Database models for accounts, the problem catalog, and personal progress."""
from datetime import date, datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    daily_goal = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    progress = db.relationship("UserProblem", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    difficulty = db.Column(db.String(12), nullable=False)
    topic = db.Column(db.String(60), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default="")
    is_seed = db.Column(db.Boolean, nullable=False, default=False)
    progress = db.relationship("UserProblem", back_populates="problem", cascade="all, delete-orphan")


class UserProblem(db.Model):
    """One user's current status for a problem; completion date supports analytics."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(12), nullable=False, default="attempted")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    solved_at = db.Column(db.DateTime(timezone=True))
    user = db.relationship("User", back_populates="progress")
    problem = db.relationship("Problem", back_populates="progress")
    __table_args__ = (
        db.UniqueConstraint("user_id", "problem_id", name="uq_user_problem"),
        db.CheckConstraint("status IN ('solved', 'attempted', 'bookmarked')", name="ck_user_problem_status"),
    )


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
