# CodeMentor AI

CodeMentor AI is a developer-focused DSA learning workspace built with Flask, SQLite, and vanilla HTML/CSS/JavaScript. The current foundation includes secure account registration and login, protected user-specific dashboards, and database-backed learning summary cards. The problem library, tracking workflows, analytics charts, recommendations, settings, and optional AI tutor are planned next; the navigation labels marked “SOON” are not implemented yet.

## Quick start

Requires Python 3.10 or newer.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `SECRET_KEY` in `.env` to a long random value before using the app beyond local development. Set `DATABASE_URL` only if you want a different database; the default is a SQLite file under `instance/`.

```powershell
$env:FLASK_APP = "run.py"
flask init-db
flask run
```

Open <http://127.0.0.1:5000>, create an account, and view the dashboard. `flask init-db` is safe to run on a fresh database and creates missing tables. For schema changes after the foundation, add Flask-Migrate rather than relying on `create_all` to alter existing tables.

## Features in this foundation

- Registration and login with Werkzeug password hashing, duplicate identity checks, and server-side validation.
- Flask-Login protected dashboard and POST-only, CSRF-protected logout.
- CSRF protection for all form submissions, secure session cookie defaults, and local-only post-login redirects.
- Per-account dashboard metrics based on stored progress records, including streak, daily goal, and solved topics.
- Responsive dark navy interface with keyboard-friendly form labels and new-account empty state.

No sample problems are seeded yet, so a new account correctly starts at zero. Later demo problems will be marked as seed data.

## Architecture

```text
codementor/
  auth/routes.py       Registration, login, logout
  dashboard/routes.py  Authenticated dashboard queries
  extensions.py        SQLAlchemy, LoginManager, CSRF
  models.py            User, Problem, UserProblem
  config.py            Environment-backed settings
  templates/           Jinja layouts, auth pages, dashboard
  static/css/app.css   Responsive visual system
run.py                 Flask entry point
tests/                 Automated route and data tests
```

`create_app()` owns extension and blueprint setup so tests can use an isolated in-memory database. `UserProblem` stores one current status per user/problem pair, allowing analytics to stay scoped to the signed-in account.

## Tests

```powershell
python -m pytest
```

## Screenshots guidance

Run the app, register a demo account, and capture the dashboard at desktop and mobile widths. For a populated portfolio screenshot, add clearly labeled seed problems and mark a few as solved after the tracking feature lands. Do not include real user email addresses or credentials in screenshots.

## Deployment

Use a production WSGI server such as Gunicorn behind a TLS reverse proxy. Set a strong `SECRET_KEY`, a persistent `DATABASE_URL`, and `FLASK_DEBUG=0` in the hosting environment. Do not commit `.env` or the SQLite database. SQLite is suitable for a single-instance demo; use a managed database when deploying multiple application instances. The optional AI tutor will use a provider-independent backend service and read credentials only from environment variables; there is no AI credential required by this foundation.
