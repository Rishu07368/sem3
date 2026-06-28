"""
Database Models
SQLAlchemy models for the timetable application.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DailySchedule(db.Model):
    """Stores generated daily schedules."""
    __tablename__ = 'daily_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    mode = db.Column(db.String(20), default='normal')  # normal, amcat, exam
    total_study_minutes = db.Column(db.Integer, default=0)
    completion_percentage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    study_blocks = db.relationship('StudyBlock', back_populates='schedule', lazy='dynamic', cascade='all, delete-orphan')
    fixed_slots = db.relationship('FixedTimeSlot', back_populates='schedule', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'mode': self.mode,
            'total_study_minutes': self.total_study_minutes,
            'completion_percentage': self.completion_percentage,
            'study_blocks': [sb.to_dict() for sb in self.study_blocks.all()],
            'fixed_slots': [fs.to_dict() for fs in self.fixed_slots.all()],
        }


class FixedTimeSlot(db.Model):
    """Stores fixed time slots for a day."""
    __tablename__ = 'fixed_time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('daily_schedules.id'), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM
    end_time = db.Column(db.String(5), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    flexible_end = db.Column(db.String(5), nullable=True)
    
    schedule = db.relationship('DailySchedule', back_populates='fixed_slots')
    
    def to_dict(self):
        return {
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'activity': self.activity,
            'flexible_end': self.flexible_end,
        }


class StudyBlock(db.Model):
    """Stores study blocks for a day."""
    __tablename__ = 'study_blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('daily_schedules.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    is_amcat = db.Column(db.Boolean, default=False)
    is_revision = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    
    # Completion tracking
    completed = db.Column(db.Boolean, default=False)
    actual_start_time = db.Column(db.DateTime, nullable=True)
    actual_end_time = db.Column(db.DateTime, nullable=True)
    actual_duration_minutes = db.Column(db.Integer, nullable=True)
    xp_earned = db.Column(db.Integer, default=0)
    
    # Pomodoro tracking
    pomodoro_sessions = db.Column(db.Integer, default=0)
    interrupted = db.Column(db.Integer, default=0)
    
    # Relationships
    schedule = db.relationship('DailySchedule', back_populates='study_blocks')
    pomodoro_sess = db.relationship('PomodoroSession', back_populates='study_block_rel', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'topic': self.topic,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_minutes': self.duration_minutes,
            'is_amcat': self.is_amcat,
            'is_revision': self.is_revision,
            'order_index': self.order_index,
            'completed': self.completed,
            'actual_duration_minutes': self.actual_duration_minutes,
            'xp_earned': self.xp_earned,
            'pomodoro_sessions': self.pomodoro_sessions,
            'interrupted': self.interrupted,
        }


class SubjectProgress(db.Model):
    """Tracks progress for each subject."""
    __tablename__ = 'subject_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), unique=True, nullable=False)
    total_topics = db.Column(db.Integer, default=0)
    completed_topics = db.Column(db.Text, default='[]')  # JSON array
    confidence_scores = db.Column(db.Text, default='{}')  # JSON object
    
    def to_dict(self):
        import json
        return {
            'subject_name': self.subject_name,
            'total_topics': self.total_topics,
            'completed_topics': json.loads(self.completed_topics or '[]'),
            'confidence_scores': json.loads(self.confidence_scores or '{}'),
        }


class MissedTask(db.Model):
    """Stores missed tasks for rescheduling."""
    __tablename__ = 'missed_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    original_date = db.Column(db.Date, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    rescheduled = db.Column(db.Boolean, default=False)
    rescheduled_to = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_date': self.original_date.isoformat(),
            'subject': self.subject,
            'topic': self.topic,
            'rescheduled': self.rescheduled,
            'rescheduled_to': self.rescheduled_to.isoformat() if self.rescheduled_to else None,
        }


class PomodoroSession(db.Model):
    """Stores individual pomodoro sessions."""
    __tablename__ = 'pomodoro_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    study_block_id = db.Column(db.Integer, db.ForeignKey('study_blocks.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, paused, interrupted
    session_type = db.Column(db.String(20), default='focus')  # focus, short_break, long_break
    
    study_block_rel = db.relationship('StudyBlock', back_populates='pomodoro_sess')
    
    def to_dict(self):
        return {
            'id': self.id,
            'study_block_id': self.study_block_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'session_type': self.session_type,
        }


class DailyMetrics(db.Model):
    """Stores daily metrics for analytics."""
    __tablename__ = 'daily_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    
    # Time metrics
    total_study_minutes = db.Column(db.Integer, default=0)
    productive_minutes = db.Column(db.Integer, default=0)
    distraction_minutes = db.Column(db.Integer, default=0)
    
    # Subject breakdown
    subject_minutes = db.Column(db.Text, default='{}')  # JSON {subject: minutes}
    
    # Completion metrics
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_missed = db.Column(db.Integer, default=0)
    tasks_rescheduled = db.Column(db.Integer, default=0)
    
    # Quality metrics
    xp_earned = db.Column(db.Integer, default=0)
    streak_count = db.Column(db.Integer, default=0)
    
    # Mood and energy (1-5 scale)
    mood_rating = db.Column(db.Integer, nullable=True)
    energy_rating = db.Column(db.Integer, nullable=True)
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_study_minutes': self.total_study_minutes,
            'productive_minutes': self.productive_minutes,
            'distraction_minutes': self.distraction_minutes,
            'subject_minutes': json.loads(self.subject_minutes or '{}'),
            'tasks_completed': self.tasks_completed,
            'tasks_missed': self.tasks_missed,
            'tasks_rescheduled': self.tasks_rescheduled,
            'xp_earned': self.xp_earned,
            'streak_count': self.streak_count,
            'mood_rating': self.mood_rating,
            'energy_rating': self.energy_rating,
            'notes': self.notes,
        }


class Configuration(db.Model):
    """Stores application configuration."""
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat(),
        }


class UserPreferences(db.Model):
    """Stores user preferences and settings."""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
        }