"""
Database Models
SQLAlchemy models for S3OS - Academic Operating System
"""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Date, Text,
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class StudyMode(str, enum.Enum):
    """Study mode enumeration."""
    NORMAL = "normal"
    AMCAT = "amcat"
    EXAM = "exam"


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    schedules: Mapped[List["DailySchedule"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    study_blocks: Mapped[List["StudyBlock"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subject_progress: Mapped[List["SubjectProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    daily_metrics: Mapped[List["DailyMetrics"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[List["UserAchievement"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    pomodoro_sessions: Mapped[List["PomodoroSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    missed_tasks: Mapped[List["MissedTask"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "xp": self.xp,
            "level": self.level,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DailySchedule(Base):
    """Stores generated daily schedules."""
    __tablename__ = "daily_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(20), default="normal")
    total_study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    mood_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    energy_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="schedules")
    fixed_slots: Mapped[List["FixedTimeSlot"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")
    study_blocks: Mapped[List["StudyBlock"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "mode": self.mode,
            "total_study_minutes": self.total_study_minutes,
            "completion_percentage": self.completion_percentage,
            "mood_rating": self.mood_rating,
            "energy_rating": self.energy_rating,
            "notes": self.notes,
            "study_blocks": [sb.to_dict() for sb in self.study_blocks],
            "fixed_slots": [fs.to_dict() for fs in self.fixed_slots],
        }


class FixedTimeSlot(Base):
    """Stores fixed time slots for a day."""
    __tablename__ = "fixed_time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("daily_schedules.id"), nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    activity: Mapped[str] = mapped_column(String(100), nullable=False)
    flexible_end: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)

    schedule: Mapped["DailySchedule"] = relationship(back_populates="fixed_slots")

    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "activity": self.activity,
            "flexible_end": self.flexible_end,
        }


class StudyBlock(Base):
    """Stores study blocks for a day."""
    __tablename__ = "study_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("daily_schedules.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_amcat: Mapped[bool] = mapped_column(Boolean, default=False)
    is_revision: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Completion tracking
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    # Pomodoro tracking
    pomodoro_sessions: Mapped[int] = mapped_column(Integer, default=0)
    interrupted: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="study_blocks")
    schedule: Mapped[Optional["DailySchedule"]] = relationship(back_populates="study_blocks")
    pomodoro_sessions_rel: Mapped[List["PomodoroSession"]] = relationship(back_populates="study_block", cascade="all, delete-orphan")
    revision_sessions: Mapped[List["RevisionSession"]] = relationship(back_populates="study_block", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "schedule_id": self.schedule_id,
            "subject": self.subject,
            "topic": self.topic,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "is_amcat": self.is_amcat,
            "is_revision": self.is_revision,
            "order_index": self.order_index,
            "completed": self.completed,
            "actual_start_time": self.actual_start_time.isoformat() if self.actual_start_time else None,
            "actual_end_time": self.actual_end_time.isoformat() if self.actual_end_time else None,
            "actual_duration_minutes": self.actual_duration_minutes,
            "xp_earned": self.xp_earned,
            "pomodoro_sessions": self.pomodoro_sessions,
            "interrupted": self.interrupted,
        }


class Subject(Base):
    """Subject master data."""
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    difficulty: Mapped[float] = mapped_column(Float, default=5.0)
    placement_importance: Mapped[float] = mapped_column(Float, default=5.0)
    target_hours_min: Mapped[float] = mapped_column(Float, default=1.0)
    target_hours_max: Mapped[float] = mapped_column(Float, default=2.0)
    is_amcat_subject: Mapped[bool] = mapped_column(Boolean, default=False)
    topics: Mapped[str] = mapped_column(Text, default="[]")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "difficulty": self.difficulty,
            "placement_importance": self.placement_importance,
            "target_hours_min": self.target_hours_min,
            "target_hours_max": self.target_hours_max,
            "is_amcat_subject": self.is_amcat_subject,
            "topics": json.loads(self.topics or "[]"),
        }


class SubjectProgress(Base):
    """Tracks progress for each subject per user."""
    __tablename__ = "subject_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_topics: Mapped[int] = mapped_column(Integer, default=0)
    completed_topics: Mapped[str] = mapped_column(Text, default="[]")
    confidence_scores: Mapped[str] = mapped_column(Text, default="{}")
    weak_topics: Mapped[str] = mapped_column(Text, default="[]")
    total_study_hours: Mapped[float] = mapped_column(Float, default=0.0)
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    last_studied: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="subject_progress")

    def to_dict(self):
        import json
        completed = json.loads(self.completed_topics or "[]")
        total = self.total_topics if self.total_topics > 0 else 1
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subject_name": self.subject_name,
            "total_topics": self.total_topics,
            "completed_topics": completed,
            "completion_percentage": (len(completed) / total) * 100 if total > 0 else 0,
            "confidence_scores": json.loads(self.confidence_scores or "{}"),
            "weak_topics": json.loads(self.weak_topics or "[]"),
            "total_study_hours": self.total_study_hours,
            "revision_count": self.revision_count,
            "last_studied": self.last_studied.isoformat() if self.last_studied else None,
        }


class RevisionSession(Base):
    """Tracks revision sessions for spaced repetition."""
    __tablename__ = "revision_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    study_block_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("study_blocks.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    interval: Mapped[int] = mapped_column(Integer, default=1)
    next_revision_date: Mapped[date] = mapped_column(Date, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    last_reviewed: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    study_block: Mapped[Optional["StudyBlock"]] = relationship(back_populates="revision_sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "study_block_id": self.study_block_id,
            "subject": self.subject,
            "topic": self.topic,
            "interval": self.interval,
            "next_revision_date": self.next_revision_date.isoformat(),
            "repetitions": self.repetitions,
            "ease_factor": self.ease_factor,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "confidence": self.confidence,
        }


class MissedTask(Base):
    """Stores missed tasks for rescheduling."""
    __tablename__ = "missed_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    original_date: Mapped[date] = mapped_column(Date, nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    rescheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    rescheduled_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="missed_tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "original_date": self.original_date.isoformat(),
            "subject": self.subject,
            "topic": self.topic,
            "rescheduled": self.rescheduled,
            "rescheduled_to": self.rescheduled_to.isoformat() if self.rescheduled_to else None,
        }


class PomodoroSession(Base):
    """Stores individual pomodoro sessions."""
    __tablename__ = "pomodoro_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    study_block_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("study_blocks.id"), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    session_type: Mapped[str] = mapped_column(String(20), default="focus")
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="pomodoro_sessions")
    study_block: Mapped[Optional["StudyBlock"]] = relationship(back_populates="pomodoro_sessions_rel")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "study_block_id": self.study_block_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "session_type": self.session_type,
            "xp_earned": self.xp_earned,
        }


class DailyMetrics(Base):
    """Stores daily metrics for analytics."""
    __tablename__ = "daily_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Time metrics
    total_study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    productive_minutes: Mapped[int] = mapped_column(Integer, default=0)
    distraction_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Subject breakdown
    subject_minutes: Mapped[str] = mapped_column(Text, default="{}")
    
    # Completion metrics
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_missed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_rescheduled: Mapped[int] = mapped_column(Integer, default=0)
    
    # Quality metrics
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Mood and energy
    mood_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    energy_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="daily_metrics")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "total_study_minutes": self.total_study_minutes,
            "productive_minutes": self.productive_minutes,
            "distraction_minutes": self.distraction_minutes,
            "subject_minutes": json.loads(self.subject_minutes or "{}"),
            "tasks_completed": self.tasks_completed,
            "tasks_missed": self.tasks_missed,
            "tasks_rescheduled": self.tasks_rescheduled,
            "xp_earned": self.xp_earned,
            "streak_count": self.streak_count,
            "mood_rating": self.mood_rating,
            "energy_rating": self.energy_rating,
            "notes": self.notes,
        }


class Achievement(Base):
    """Achievement definitions."""
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    icon: Mapped[str] = mapped_column(String(50), default="trophy")
    category: Mapped[str] = mapped_column(String(50), default="general")
    requirement_type: Mapped[str] = mapped_column(String(50), default="count")
    requirement_value: Mapped[int] = mapped_column(Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "xp_reward": self.xp_reward,
            "icon": self.icon,
            "category": self.category,
            "requirement_type": self.requirement_type,
            "requirement_value": self.requirement_value,
        }


class UserAchievement(Base):
    """User-earned achievements."""
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship()

    def to_dict(self):
        return {
            "id": self.id,
            "achievement": self.achievement.to_dict() if self.achievement else None,
            "earned_at": self.earned_at.isoformat(),
        }


class Notification(Base):
    """User notifications."""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }


class Configuration(Base):
    """Stores application configuration."""
    __tablename__ = "configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat(),
        }


class UserPreferences(Base):
    """Stores user preferences and settings."""
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
        }
