from codementor.extensions import db
from codementor.models import User


def test_register_hashes_password_and_logs_user_in(client, app):
    response = client.post("/auth/register", data={
        "username": "learner_1", "email": "learner@example.com", "password": "secure-pass-1"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Good to see you, learner_1" in response.data
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.email == "learner@example.com"))
        assert user is not None
        assert user.password_hash != "secure-pass-1"
        assert user.check_password("secure-pass-1")


def test_rejects_short_password_and_duplicate_email(client):
    payload = {"username": "learner", "email": "learner@example.com", "password": "secure-pass"}
    response = client.post("/auth/register", data={**payload, "password": "short"})
    assert b"at least 8 characters" in response.data
    assert client.post("/auth/register", data=payload).status_code == 302
    client.post("/auth/logout")
    assert b"already registered" in client.post("/auth/register", data={**payload, "username": "learner2"}).data


def test_private_dashboard_requires_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_login_logout_flow(client):
    client.post("/auth/register", data={"username": "learner", "email": "l@example.com", "password": "secure-pass"})
    client.post("/auth/logout")
    response = client.post("/auth/login", data={"identity": "l@example.com", "password": "secure-pass"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Good to see you, learner" in response.data
