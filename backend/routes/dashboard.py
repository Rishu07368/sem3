"""
Dashboard routes - Main dashboard data and overview.
"""
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models.database import User, DailySchedule, StudyBlock, DailyMetrics, SubjectProgress, MissedTask
from utils.security import get_current_user
from services.analytics_engine import AnalyticsEngine
from services.scheduling_engine import SchedulingEngine, SchedulingConstraints, StudyMode
from services.subjects import get_default_subjects

router = APIRouter()


class DashboardOverview(BaseModel):
    semester_progress: dict
    today_schedule: Optional[dict]
    current_streak: int
    longest_streak: int
    total_xp: int
    level: int
    todays_study_hours: float
    weekly_progress: dict
    subject_progress: List[dict]
    pending_tasks: int
    missed_tasks: int
    amcat_countdown: int


@router.get("/", response_model=DashboardOverview)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard overview data."""
    today = datetime.now().date()
    
    # Get semester progress
    start_date = datetime.strptime("2025-07-14", "%Y-%m-%d")
    end_date = datetime.strptime("2025-11-10", "%Y-%m-%d")
    
    total_days = (end_date.date() - start_date.date()).days + 1
    elapsed_days = (today - start_date.date()).days + 1
    remaining_days = total_days - elapsed_days
    
    # AMCAT countdown
    amcat_start = datetime.strptime("2025-08-15", "%Y-%m-%d").date()
    amcat_countdown = max(0, (amcat_start - today).days)
    
    # Get today's schedule
    schedule = db.query(DailySchedule).filter(
        DailySchedule.user_id == current_user.id,
        DailySchedule.date == today
    ).first()
    
    # Get subject progress
    progress_list = db.query(SubjectProgress).filter(
        SubjectProgress.user_id == current_user.id
    ).all()
    
    subject_progress = []
    for p in progress_list:
        import json
        completed = json.loads(p.completed_topics or "[]")
        total = p.total_topics if p.total_topics > 0 else 1
        subject_progress.append({
            "subject": p.subject_name,
            "completed": len(completed),
            "total": p.total_topics,
            "percentage": (len(completed) / total) * 100,
            "study_hours": p.total_study_hours,
        })
    
    # Get pending and missed tasks
    pending = db.query(StudyBlock).filter(
        StudyBlock.user_id == current_user.id,
        StudyBlock.completed == False,
        StudyBlock.start_time <= datetime.now().strftime("%H:%M")
    ).count()
    
    missed = db.query(MissedTask).filter(
        MissedTask.user_id == current_user.id,
        MissedTask.rescheduled == False
    ).count()
    
    # Weekly progress
    week_start = today - timedelta(days=today.weekday())
    weekly_metrics = db.query(DailyMetrics).filter(
        DailyMetrics.user_id == current_user.id,
        DailyMetrics.date >= week_start,
        DailyMetrics.date <= today
    ).all()
    
    weekly_progress = {
        "total_minutes": sum(m.total_study_minutes for m in weekly_metrics),
        "days_active": len(weekly_metrics),
        "xp_earned": sum(m.xp_earned for m in weekly_metrics),
    }
    
    # Today's study hours
    today_metrics = db.query(DailyMetrics).filter(
        DailyMetrics.user_id == current_user.id,
        DailyMetrics.date == today
    ).first()
    
    todays_study_hours = today_metrics.total_study_minutes / 60 if today_metrics else 0
    
    return {
        "semester_progress": {
            "total_days": total_days,
            "elapsed_days": max(0, elapsed_days),
            "remaining_days": max(0, remaining_days),
            "progress_percentage": (max(0, elapsed_days) / total_days) * 100 if total_days > 0 else 0,
        },
        "today_schedule": schedule.to_dict() if schedule else None,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak,
        "total_xp": current_user.xp,
        "level": current_user.level,
        "todays_study_hours": todays_study_hours,
        "weekly_progress": weekly_progress,
        "subject_progress": subject_progress,
        "pending_tasks": pending,
        "missed_tasks": missed,
        "amcat_countdown": amcat_countdown,
    }


@router.get("/quick-stats")
def get_quick_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quick stats for the dashboard header."""
    today = datetime.now().date()
    
    # Today's metrics
    today_metrics = db.query(DailyMetrics).filter(
        DailyMetrics.user_id == current_user.id,
        DailyMetrics.date == today
    ).first()
    
    # Week start
    week_start = today - timedelta(days=today.weekday())
    weekly_metrics = db.query(DailyMetrics).filter(
        DailyMetrics.user_id == current_user.id,
        DailyMetrics.date >= week_start,
        DailyMetrics.date <= today
    ).all()
    
    return {
        "today_study_minutes": today_metrics.total_study_minutes if today_metrics else 0,
        "week_study_minutes": sum(m.total_study_minutes for m in weekly_metrics),
        "current_streak": current_user.current_streak,
        "xp": current_user.xp,
        "level": current_user.level,
    }


@router.get("/heatmap/{year}/{month}")
def get_heatmap(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get study heatmap for a month."""
    analytics = AnalyticsEngine(db, current_user.id)
    return {"heatmap": analytics.get_study_heatmap(year, month)}
