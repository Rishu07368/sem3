"""
Analytics routes - Reports and insights.
"""
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.database import User
from utils.security import get_current_user
from services.analytics_engine import AnalyticsEngine

router = APIRouter()


@router.get("/daily/{date_str}")
def get_daily_analytics(
    date_str: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific date."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_daily_analytics(date_obj)


@router.get("/weekly/{start_date}")
def get_weekly_analytics(
    start_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a week."""
    date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_weekly_analytics(date_obj)


@router.get("/monthly/{year}/{month}")
def get_monthly_analytics(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a month."""
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_monthly_analytics(year, month)


@router.get("/semester")
def get_semester_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive semester analytics."""
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_semester_analytics()


@router.get("/heatmap/{year}/{month}")
def get_study_heatmap(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get study heatmap for a month."""
    analytics = AnalyticsEngine(db, current_user.id)
    return {"data": analytics.get_study_heatmap(year, month)}


@router.get("/subjects/distribution")
def get_subject_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get study time distribution by subject."""
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_subject_distribution()


@router.get("/amcat/readiness")
def get_amcat_readiness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AMCAT readiness assessment."""
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_amcat_readiness()


@router.get("/projections")
def get_projections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get projected completion dates."""
    analytics = AnalyticsEngine(db, current_user.id)
    return {"projections": analytics.get_projected_completion()}


@router.get("/burndown")
def get_burndown_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get burn-down chart data."""
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_burndown_chart()
