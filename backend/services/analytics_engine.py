"""
Analytics Engine
Provides comprehensive analytics and reporting for study progress.
"""
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from collections import defaultdict
import json

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.database import (
    DailyMetrics, StudyBlock, SubjectProgress, User,
    PomodoroSession, Achievement, UserAchievement
)


class AnalyticsEngine:
    """
    Provides analytics and insights for study progress.
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def get_daily_analytics(self, target_date: date) -> Dict:
        """Get analytics for a specific date."""
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date == target_date
        ).first()
        
        blocks = self.db.query(StudyBlock).filter(
            StudyBlock.user_id == self.user_id
        ).all()
        
        # Filter blocks for this date
        date_blocks = [
            b for b in blocks
            if b.created_at and b.created_at.date() == target_date
        ]
        
        completed = [b for b in date_blocks if b.completed]
        total_duration = sum(b.duration_minutes for b in date_blocks)
        completed_duration = sum(b.actual_duration_minutes for b in completed if b.actual_duration_minutes)
        
        return {
            "date": target_date.isoformat(),
            "total_study_minutes": total_duration,
            "completed_study_minutes": completed_duration,
            "blocks_completed": len(completed),
            "blocks_total": len(date_blocks),
            "completion_rate": (len(completed) / len(date_blocks) * 100) if date_blocks else 0,
            "mood_rating": metrics.mood_rating if metrics else None,
            "energy_rating": metrics.energy_rating if metrics else None,
            "xp_earned": metrics.xp_earned if metrics else 0,
            "tasks_completed": metrics.tasks_completed if metrics else 0,
            "tasks_missed": metrics.tasks_missed if metrics else 0,
        }
    
    def get_weekly_analytics(self, start_date: date) -> Dict:
        """Get analytics for a week starting from start_date."""
        end_date = start_date + timedelta(days=6)
        
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        ).all()
        
        total_study_minutes = sum(m.total_study_minutes for m in metrics)
        total_xp = sum(m.xp_earned for m in metrics)
        total_completed = sum(m.tasks_completed for m in metrics)
        total_missed = sum(m.tasks_missed for m in metrics)
        
        # Study hours per day
        daily_breakdown = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_metrics = next((m for m in metrics if m.date == day), None)
            if day_metrics:
                daily_breakdown.append({
                    "date": day.isoformat(),
                    "minutes": day_metrics.total_study_minutes,
                    "xp": day_metrics.xp_earned,
                })
            else:
                daily_breakdown.append({
                    "date": day.isoformat(),
                    "minutes": 0,
                    "xp": 0,
                })
        
        # Subject distribution
        subject_minutes = defaultdict(int)
        for m in metrics:
            sm = json.loads(m.subject_minutes or "{}")
            for subject, minutes in sm.items():
                subject_minutes[subject] += minutes
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_study_minutes": total_study_minutes,
            "total_study_hours": total_study_minutes / 60,
            "average_daily_hours": (total_study_minutes / 60 / 7) if metrics else 0,
            "total_xp": total_xp,
            "tasks_completed": total_completed,
            "tasks_missed": total_missed,
            "daily_breakdown": daily_breakdown,
            "subject_distribution": dict(subject_minutes),
        }
    
    def get_monthly_analytics(self, year: int, month: int) -> Dict:
        """Get analytics for a specific month."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        ).all()
        
        total_study_minutes = sum(m.total_study_minutes for m in metrics)
        total_xp = sum(m.xp_earned for m in metrics)
        
        # Calculate streak
        user = self.db.query(User).filter(User.id == self.user_id).first()
        
        return {
            "year": year,
            "month": month,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_study_minutes": total_study_minutes,
            "total_study_hours": total_study_minutes / 60,
            "total_xp": total_xp,
            "days_active": len(metrics),
            "days_in_month": end_date.day,
            "current_streak": user.current_streak if user else 0,
            "longest_streak": user.longest_streak if user else 0,
        }
    
    def get_semester_analytics(self) -> Dict:
        """Get comprehensive semester analytics."""
        # Get all metrics
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id
        ).all()
        
        total_study_minutes = sum(m.total_study_minutes for m in metrics)
        total_xp = sum(m.xp_earned for m in metrics)
        total_completed = sum(m.tasks_completed for m in metrics)
        total_missed = sum(m.tasks_missed for m in metrics)
        
        user = self.db.query(User).filter(User.id == self.user_id).first()
        
        # Subject progress
        subject_progress = self.db.query(SubjectProgress).filter(
            SubjectProgress.user_id == self.user_id
        ).all()
        
        subject_completion = {}
        for sp in subject_progress:
            completed = json.loads(sp.completed_topics or "[]")
            total = sp.total_topics if sp.total_topics > 0 else 1
            subject_completion[sp.subject_name] = {
                "completed": len(completed),
                "total": sp.total_topics,
                "percentage": (len(completed) / total) * 100,
                "study_hours": sp.total_study_hours,
            }
        
        # Weekly trend
        weekly_data = []
        for week in range(0, 16):  # ~16 weeks in semester
            week_start = date(2025, 7, 14) + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            week_metrics = [
                m for m in metrics
                if week_start <= m.date <= week_end
            ]
            weekly_data.append({
                "week": week + 1,
                "study_minutes": sum(m.total_study_minutes for m in week_metrics),
            })
        
        return {
            "total_study_minutes": total_study_minutes,
            "total_study_hours": total_study_minutes / 60,
            "average_daily_hours": (total_study_minutes / 60 / max(1, len(metrics))),
            "total_xp": total_xp,
            "level": user.level if user else 1,
            "tasks_completed": total_completed,
            "tasks_missed": total_missed,
            "completion_rate": (total_completed / (total_completed + total_missed) * 100)
                if (total_completed + total_missed) > 0 else 0,
            "current_streak": user.current_streak if user else 0,
            "longest_streak": user.longest_streak if user else 0,
            "subject_completion": subject_completion,
            "weekly_trend": weekly_data,
        }
    
    def get_study_heatmap(self, year: int, month: int) -> List[Dict]:
        """Get study heatmap data for a month (GitHub-style)."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        ).all()
        
        metrics_dict = {m.date: m for m in metrics}
        
        heatmap = []
        for day_num in range(1, end_date.day + 1):
            day_date = date(year, month, day_num)
            metric = metrics_dict.get(day_date)
            
            minutes = metric.total_study_minutes if metric else 0
            
            # Intensity levels (0-4)
            if minutes == 0:
                intensity = 0
            elif minutes < 30:
                intensity = 1
            elif minutes < 60:
                intensity = 2
            elif minutes < 120:
                intensity = 3
            else:
                intensity = 4
            
            heatmap.append({
                "date": day_date.isoformat(),
                "minutes": minutes,
                "intensity": intensity,
                "weekday": day_date.weekday(),
            })
        
        return heatmap
    
    def get_subject_distribution(self) -> Dict:
        """Get study time distribution by subject."""
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id
        ).all()
        
        subject_totals = defaultdict(int)
        for m in metrics:
            sm = json.loads(m.subject_minutes or "{}")
            for subject, minutes in sm.items():
                subject_totals[subject] += minutes
        
        total = sum(subject_totals.values())
        
        distribution = []
        for subject, minutes in sorted(subject_totals.items(), key=lambda x: -x[1]):
            distribution.append({
                "subject": subject,
                "minutes": minutes,
                "hours": minutes / 60,
                "percentage": (minutes / total * 100) if total > 0 else 0,
            })
        
        return {
            "total_minutes": total,
            "total_hours": total / 60,
            "distribution": distribution,
        }
    
    def get_amcat_readiness(self) -> Dict:
        """Calculate AMCAT readiness score."""
        # Get AMCAT-related study blocks
        amcat_blocks = self.db.query(StudyBlock).filter(
            StudyBlock.user_id == self.user_id,
            StudyBlock.is_amcat == True
        ).all()
        
        completed = [b for b in amcat_blocks if b.completed]
        
        # Get subject progress for core AMCAT topics
        subjects = ["ADSA", "DBMS", "COA"]
        subject_progress = {}
        
        for subj in subjects:
            sp = self.db.query(SubjectProgress).filter(
                SubjectProgress.user_id == self.user_id,
                SubjectProgress.subject_name == subj
            ).first()
            
            if sp:
                completed_topics = json.loads(sp.completed_topics or "[]")
                total = sp.total_topics if sp.total_topics > 0 else 1
                subject_progress[subj] = (len(completed_topics) / total) * 100
            else:
                subject_progress[subj] = 0
        
        avg_core_progress = sum(subject_progress.values()) / len(subject_progress) if subject_progress else 0
        
        # Calculate overall readiness
        amcat_completion = (len(completed) / len(amcat_blocks) * 100) if amcat_blocks else 0
        
        readiness_score = (
            amcat_completion * 0.4 +
            avg_core_progress * 0.6
        )
        
        return {
            "amcat_practice_completed": len(completed),
            "amcat_practice_total": len(amcat_blocks),
            "amcat_practice_percentage": amcat_completion,
            "core_subject_progress": subject_progress,
            "avg_core_progress": avg_core_progress,
            "overall_readiness": readiness_score,
            "status": (
                "Ready" if readiness_score >= 80
                else "Almost There" if readiness_score >= 60
                else "In Progress"
            ),
        }
    
    def get_projected_completion(self) -> Dict:
        """Project when syllabus will be completed at current pace."""
        subject_progress = self.db.query(SubjectProgress).filter(
            SubjectProgress.user_id == self.user_id
        ).all()
        
        projections = {}
        
        for sp in subject_progress:
            completed = json.loads(sp.completed_topics or "[]")
            remaining = sp.total_topics - len(completed)
            
            if remaining <= 0:
                projections[sp.subject_name] = {
                    "status": "Completed",
                    "remaining_topics": 0,
                    "projected_completion": "Now",
                }
                continue
            
            # Calculate weekly study rate
            weeks_studied = 1  # Minimum
            if sp.total_study_hours > 0:
                weeks_studied = max(1, len(completed) / max(0.1, sp.total_study_hours / weeks_studied))
            
            # Assume consistent pace
            hours_per_topic = 2.0  # Average
            remaining_hours = remaining * hours_per_topic
            
            avg_weekly_hours = 5.0  # Estimate
            weeks_needed = remaining_hours / avg_weekly_hours
            
            projected_date = datetime.now().date() + timedelta(weeks=int(weeks_needed))
            
            projections[sp.subject_name] = {
                "remaining_topics": remaining,
                "hours_remaining": remaining_hours,
                "projected_completion": projected_date.isoformat(),
            }
        
        return projections
    
    def get_burndown_chart(self) -> Dict:
        """Get data for a burn-down chart."""
        # Total topics across all subjects
        subject_progress = self.db.query(SubjectProgress).filter(
            SubjectProgress.user_id == self.user_id
        ).all()
        
        total_topics = sum(sp.total_topics for sp in subject_progress)
        
        # Calculate remaining topics by date
        today = datetime.now().date()
        
        # Get completed topics from metrics
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date <= today
        ).order_by(DailyMetrics.date).all()
        
        cumulative_completed = 0
        burndown = []
        
        # Start from semester beginning
        start_date = date(2025, 7, 14)
        
        for days_since_start in range((today - start_date).days + 1):
            current_date = start_date + timedelta(days=days_since_start)
            
            # Find metrics for this date
            day_metrics = next((m for m in metrics if m.date == current_date), None)
            
            if day_metrics:
                cumulative_completed += day_metrics.tasks_completed
            
            remaining = max(0, total_topics - cumulative_completed)
            
            burndown.append({
                "date": current_date.isoformat(),
                "remaining": remaining,
                "completed": cumulative_completed,
            })
        
        return {
            "total_topics": total_topics,
            "current_remaining": remaining,
            "chart_data": burndown,
        }
