from fastapi import APIRouter, Depends
from sqlmodel import select, func
from app.db import SQLite_DB
from typing import List, Dict, Any
from datetime import date, timedelta, datetime

router = APIRouter(
    tags=["dashboard"],
    prefix="/dashboard",
)

@router.get("/stats")
def get_dashboard_stats(session: SQLite_DB.SessionDep) -> Dict[str, Any]:
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    one_week_ago = start_of_day - timedelta(days=7)

    # 1. Tasks due today and to review
    tasks_due_today = session.exec(
        select(SQLite_DB.Paper).where(SQLite_DB.Paper.due_date >= start_of_day, SQLite_DB.Paper.due_date <= end_of_day)
    ).all()
    tasks_to_review = session.exec(select(SQLite_DB.Paper).where(SQLite_DB.Paper.status == '4')).all()

    # 2. Stats cards
    pending_review_count = len(tasks_to_review)
    in_progress_count = session.exec(
        select(func.count(SQLite_DB.Paper.id)).where(SQLite_DB.Paper.status.in_(['2', '5']))
    ).one()
    completed_this_week_count = session.exec(
        select(func.count(SQLite_DB.Paper.id)).where(SQLite_DB.Paper.last_reviewed_at >= one_week_ago)
    ).one()

    stats_cards = {
        "pending_review_count": pending_review_count,
        "in_progress_count": in_progress_count,
        "completed_this_week_count": completed_this_week_count
    }

    # 3. Activity chart (last 7 days)
    activity_query = session.exec(
        select(
            func.date(SQLite_DB.Paper.last_reviewed_at),
            func.count(SQLite_DB.Paper.id)
        )
        .where(SQLite_DB.Paper.last_reviewed_at >= one_week_ago)
        .group_by(func.date(SQLite_DB.Paper.last_reviewed_at))
    ).all()
    
    activity_map = {str(d): c for d, c in activity_query}
    activity_chart_data = []
    for i in range(7):
        current_date = today - timedelta(days=i)
        date_str = current_date.isoformat()
        activity_chart_data.append({
            "date": date_str,
            "count": activity_map.get(date_str, 0)
        })
    activity_chart_data.reverse() # Order from past to present

    return {
        "tasks_due_today": tasks_due_today,
        "tasks_to_review": tasks_to_review,
        "stats_cards": stats_cards,
        "activity_chart": activity_chart_data
    }
