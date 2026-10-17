from datetime import datetime, timezone
import re

from codementor.extensions import db
from codementor.models import Problem, User, UserProblem


def _register(client, username, email):
    return client.post("/auth/register", data={"username": username, "email": email, "password": "secure-pass"})


def test_dashboard_uses_only_current_users_progress(client, app):
    _register(client, "alice", "alice@example.com")
    with app.app_context():
        alice = db.session.scalar(db.select(User).where(User.username == "alice"))
        bob = User(username="bob", email="bob@example.com")
        bob.set_password("secure-pass")
        problem = Problem(title="Array sum", slug="array-sum", topic="Arrays", difficulty="Easy")
        db.session.add_all([bob, problem])
        db.session.flush()
        db.session.add_all([
            UserProblem(user_id=alice.id, problem_id=problem.id, status="solved", solved_at=datetime.now(timezone.utc)),
            UserProblem(user_id=bob.id, problem_id=problem.id, status="solved", solved_at=datetime.now(timezone.utc)),
        ])
        db.session.commit()
    response = client.get("/")
    assert response.status_code == 200
    assert re.search(rb'class="metric-value">1<span class="metric-unit"> problems', response.data)
    assert b"Arrays" in response.data
    assert b'"labels": ["Easy"]' in response.data


def test_new_account_has_helpful_empty_state(client):
    _register(client, "newbie", "newbie@example.com")
    response = client.get("/")
    assert response.status_code == 200
    assert b"Your topic map starts here" in response.data
    assert re.search(rb'class="metric-value">0<span class="metric-unit"> problems', response.data)
    assert b'"count": 0' in response.data
