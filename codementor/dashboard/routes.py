"""Authenticated dashboard, computed from the current user's database records."""
from datetime import date, datetime, time, timedelta, timezone

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import case, func

from ..extensions import db
from ..models import Problem, UserProblem

dashboard_bp = Blueprint("dashboard", __name__)


def _utc_day_bounds(day):
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def _streak(solved_dates):
    days = set(solved_dates)
    today = date.today()
    cursor = today if today in days else today - timedelta(days=1)
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


@dashboard_bp.get("/")
@login_required
def index():
    # Outer join keeps catalog topics visible even before this user has solved one.
    rows = db.session.execute(
        db.select(Problem.topic, func.count(Problem.id),
                  func.sum(case((UserProblem.status == "solved", 1), else_=0)))
        .outerjoin(UserProblem, (UserProblem.problem_id == Problem.id) &
                   (UserProblem.user_id == current_user.id))
        .group_by(Problem.topic).order_by(func.count(Problem.id).desc(), Problem.topic).limit(8)
    ).all()
    total_solved = db.session.scalar(db.select(func.count(UserProblem.id)).where(
        UserProblem.user_id == current_user.id, UserProblem.status == "solved")) or 0
    today_start, today_end = _utc_day_bounds(date.today())
    solved_today = db.session.scalar(db.select(func.count(UserProblem.id)).where(
        UserProblem.user_id == current_user.id, UserProblem.status == "solved",
        UserProblem.solved_at >= today_start, UserProblem.solved_at < today_end)) or 0
    attempted_count = db.session.scalar(db.select(func.count(UserProblem.id)).where(
        UserProblem.user_id == current_user.id, UserProblem.status == "attempted")) or 0
    solved_dates = db.session.execute(db.select(func.date(UserProblem.solved_at)).where(
        UserProblem.user_id == current_user.id, UserProblem.status == "solved", UserProblem.solved_at.is_not(None))).scalars().all()
    solved_dates = [date.fromisoformat(value) for value in solved_dates if value]
    topic_progress = [{"topic": topic, "total": total, "solved": int(solved or 0),
                       "percent": round((int(solved or 0) / total) * 100) if total else 0}
                      for topic, total, solved in rows]
    # Build a continuous 14-day series so days without solves are represented as zero.
    activity_start = date.today() - timedelta(days=13)
    activity_start_dt, _ = _utc_day_bounds(activity_start)
    activity_rows = db.session.execute(
        db.select(func.date(UserProblem.solved_at), func.count(UserProblem.id))
        .where(UserProblem.user_id == current_user.id, UserProblem.status == "solved",
               UserProblem.solved_at >= activity_start_dt, UserProblem.solved_at < today_end)
        .group_by(func.date(UserProblem.solved_at))
    ).all()
    activity_counts = {date.fromisoformat(day): count for day, count in activity_rows if day}
    activity = [{"label": f"{(activity_start + timedelta(days=offset)):%b} {(activity_start + timedelta(days=offset)).day}",
                 "count": activity_counts.get(activity_start + timedelta(days=offset), 0)}
                for offset in range(14)]
    difficulty_rows = db.session.execute(
        db.select(Problem.difficulty, func.count(UserProblem.id))
        .join(UserProblem, UserProblem.problem_id == Problem.id)
        .where(UserProblem.user_id == current_user.id, UserProblem.status == "solved")
        .group_by(Problem.difficulty)
    ).all()
    difficulty = {"labels": [level for level, _ in difficulty_rows],
                  "values": [count for _, count in difficulty_rows]}
    return render_template("dashboard/index.html", total_solved=total_solved,
                           solved_today=solved_today, streak=_streak(solved_dates),
                           attempted_count=attempted_count, topic_progress=topic_progress,
                           activity=activity, difficulty=difficulty,
                           daily_goal=current_user.daily_goal)
