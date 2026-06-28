"""
API Routes for the Daily Timetable Engine
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models.database import (
    db, DailySchedule, FixedTimeSlot, StudyBlock, SubjectProgress,
    MissedTask, PomodoroSession, DailyMetrics, Configuration
)
from services.scheduling_engine import SchedulingEngine, SchedulingConstraints, StudyMode
from services.subjects import get_default_subjects, get_amcat_subjects

api = Blueprint('api', __name__)


# ============================================================================
# SCHEDULING ENGINE INITIALIZATION
# ============================================================================

def get_scheduling_engine():
    """Initialize the scheduling engine with current configuration."""
    # Get configuration
    start_date = datetime.strptime(
        get_config('start_date', '2025-07-14'), '%Y-%m-%d'
    ).date()
    end_date = datetime.strptime(
        get_config('end_date', '2025-11-10'), '%Y-%m-%d'
    ).date()
    
    amcat_start = get_config('amcat_start_date')
    amcat_end = get_config('amcat_end_date')
    exam_start = get_config('exam_start_date')
    
    constraints = SchedulingConstraints(
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.min.time()),
        amcat_start_date=datetime.strptime(amcat_start, '%Y-%m-%d').date() if amcat_start else None,
        amcat_end_date=datetime.strptime(amcat_end, '%Y-%m-%d').date() if amcat_end else None,
        exam_start_date=datetime.strptime(exam_start, '%Y-%m-%d').date() if exam_start else None,
    )
    
    engine = SchedulingEngine(constraints)
    
    # Add subjects
    for subject in get_default_subjects():
        engine.add_subject(subject)
    
    return engine


def get_config(key, default=None):
    """Get configuration value from database."""
    config = Configuration.query.filter_by(key=key).first()
    return config.value if config else default


def set_config(key, value):
    """Set configuration value in database."""
    config = Configuration.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Configuration(key=key, value=value)
        db.session.add(config)
    db.session.commit()


# ============================================================================
# TIMETABLE GENERATION
# ============================================================================

@api.route('/generate', methods=['POST'])
def generate_timetable():
    """Generate complete timetable for the date range."""
    engine = get_scheduling_engine()
    schedules = engine.generate_timetable()
    
    generated_count = 0
    
    for schedule in schedules:
        # Check if schedule already exists
        existing = DailySchedule.query.filter_by(date=schedule.date.date()).first()
        
        if existing:
            # Update existing schedule
            existing.mode = schedule.mode.value
            existing.total_study_minutes = schedule.total_study_minutes
            # Keep existing completion percentage
        else:
            # Create new schedule
            daily_schedule = DailySchedule(
                date=schedule.date.date(),
                mode=schedule.mode.value,
                total_study_minutes=schedule.total_study_minutes,
                completion_percentage=0.0
            )
            db.session.add(daily_schedule)
            db.session.flush()  # Get the ID
            
            # Add fixed time slots
            for slot in schedule.time_slots:
                fixed_slot = FixedTimeSlot(
                    schedule_id=daily_schedule.id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    activity=slot.activity,
                    flexible_end=slot.flexible_end
                )
                db.session.add(fixed_slot)
            
            # Add study blocks
            for idx, block in enumerate(schedule.study_blocks):
                study_block = StudyBlock(
                    schedule_id=daily_schedule.id,
                    subject=block.subject,
                    topic=block.topic,
                    start_time=block.start_time,
                    end_time=block.end_time,
                    duration_minutes=block.duration_minutes,
                    is_amcat=block.is_amcat,
                    is_revision=block.is_revision,
                    order_index=idx
                )
                db.session.add(study_block)
            
            generated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Generated {generated_count} new daily schedules',
        'total_schedules': DailySchedule.query.count()
    })


@api.route('/schedule/<date>', methods=['GET'])
def get_schedule(date):
    """Get schedule for a specific date."""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    schedule = DailySchedule.query.filter_by(date=date_obj).first()
    
    if not schedule:
        # Generate schedule for this date
        engine = get_scheduling_engine()
        schedule_data = engine.generate_daily_schedule(
            datetime.combine(date_obj, datetime.min.time())
        )
        
        # Create in database
        daily_schedule = DailySchedule(
            date=date_obj,
            mode=schedule_data.mode.value,
            total_study_minutes=schedule_data.total_study_minutes
        )
        db.session.add(daily_schedule)
        db.session.flush()
        
        # Add fixed slots and study blocks
        for slot in schedule_data.time_slots:
            fixed_slot = FixedTimeSlot(
                schedule_id=daily_schedule.id,
                start_time=slot.start_time,
                end_time=slot.end_time,
                activity=slot.activity,
                flexible_end=slot.flexible_end
            )
            db.session.add(fixed_slot)
        
        for idx, block in enumerate(schedule_data.study_blocks):
            study_block = StudyBlock(
                schedule_id=daily_schedule.id,
                subject=block.subject,
                topic=block.topic,
                start_time=block.start_time,
                end_time=block.end_time,
                duration_minutes=block.duration_minutes,
                is_amcat=block.is_amcat,
                is_revision=block.is_revision,
                order_index=idx
            )
            db.session.add(study_block)
        
        db.session.commit()
        return jsonify(daily_schedule.to_dict())
    
    return jsonify(schedule.to_dict())


@api.route('/schedules', methods=['GET'])
def get_schedules():
    """Get all schedules with optional filtering."""
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = DailySchedule.query
    
    if start:
        query = query.filter(DailySchedule.date >= datetime.strptime(start, '%Y-%m-%d').date())
    if end:
        query = query.filter(DailySchedule.date <= datetime.strptime(end, '%Y-%m-%d').date())
    
    schedules = query.order_by(DailySchedule.date).all()
    
    return jsonify({
        'schedules': [s.to_dict() for s in schedules],
        'count': len(schedules)
    })


# ============================================================================
# STUDY BLOCK MANAGEMENT
# ============================================================================

@api.route('/blocks/<int:block_id>', methods=['GET'])
def get_block(block_id):
    """Get a specific study block."""
    block = StudyBlock.query.get_or_404(block_id)
    return jsonify(block.to_dict())


@api.route('/blocks/<int:block_id>/complete', methods=['POST'])
def complete_block(block_id):
    """Mark a study block as completed."""
    block = StudyBlock.query.get_or_404(block_id)
    data = request.get_json() or {}
    
    block.completed = True
    block.actual_end_time = datetime.utcnow()
    
    if block.actual_start_time:
        actual_duration = (block.actual_end_time - block.actual_start_time).total_seconds() / 60
        block.actual_duration_minutes = int(actual_duration)
    
    # Calculate XP earned
    base_xp = block.duration_minutes * 2  # 2 XP per minute
    if block.is_revision:
        base_xp *= 1.5  # 50% bonus for revision
    if block.is_amcat:
        base_xp *= 1.2  # 20% bonus for AMCAT
    
    block.xp_earned = int(base_xp)
    
    # Update daily metrics
    schedule = block.schedule
    metrics = DailyMetrics.query.filter_by(date=schedule.date).first()
    if not metrics:
        metrics = DailyMetrics(date=schedule.date)
        db.session.add(metrics)
    
    metrics.tasks_completed += 1
    metrics.xp_earned += block.xp_earned
    metrics.total_study_minutes += block.actual_duration_minutes or block.duration_minutes
    
    # Update schedule completion percentage
    total_blocks = schedule.study_blocks.count()
    completed_blocks = schedule.study_blocks.filter_by(completed=True).count()
    schedule.completion_percentage = (completed_blocks / total_blocks * 100) if total_blocks > 0 else 0
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'xp_earned': block.xp_earned,
        'completion_percentage': schedule.completion_percentage
    })


@api.route('/blocks/<int:block_id>/miss', methods=['POST'])
def miss_block(block_id):
    """Mark a study block as missed and schedule for rescheduling."""
    block = StudyBlock.query.get_or_404(block_id)
    
    # Record missed task
    missed_task = MissedTask(
        original_date=block.schedule.date,
        subject=block.subject,
        topic=block.topic
    )
    db.session.add(missed_task)
    
    # Update daily metrics
    schedule = block.schedule
    metrics = DailyMetrics.query.filter_by(date=schedule.date).first()
    if not metrics:
        metrics = DailyMetrics(date=schedule.date)
        db.session.add(metrics)
    
    metrics.tasks_missed += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task marked as missed and queued for rescheduling',
        'missed_task_id': missed_task.id
    })


@api.route('/blocks/<int:block_id>/reschedule', methods=['POST'])
def reschedule_block(block_id):
    """Reschedule a study block to a new date."""
    block = StudyBlock.query.get_or_404(block_id)
    data = request.get_json()
    
    new_date = data.get('date')
    if not new_date:
        return jsonify({'error': 'New date is required'}), 400
    
    try:
        new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Find or create schedule for new date
    new_schedule = DailySchedule.query.filter_by(date=new_date_obj).first()
    if not new_schedule:
        # Generate schedule for new date
        engine = get_scheduling_engine()
        schedule_data = engine.generate_daily_schedule(
            datetime.combine(new_date_obj, datetime.min.time())
        )
        new_schedule = DailySchedule(
            date=new_date_obj,
            mode=schedule_data.mode.value,
            total_study_minutes=schedule_data.total_study_minutes
        )
        db.session.add(new_schedule)
        db.session.flush()
        
        # Add study blocks from engine
        for idx, block_data in enumerate(schedule_data.study_blocks):
            study_block = StudyBlock(
                schedule_id=new_schedule.id,
                subject=block_data.subject,
                topic=block_data.topic,
                start_time=block_data.start_time,
                end_time=block_data.end_time,
                duration_minutes=block_data.duration_minutes,
                is_amcat=block_data.is_amcat,
                is_revision=block_data.is_revision,
                order_index=idx
            )
            db.session.add(study_block)
    
    # Mark original missed task as rescheduled
    missed_task = MissedTask.query.filter_by(
        original_date=block.schedule.date,
        subject=block.subject,
        topic=block.topic,
        rescheduled=False
    ).first()
    
    if missed_task:
        missed_task.rescheduled = True
        missed_task.rescheduled_to = new_date_obj
    
    # Update metrics
    old_metrics = DailyMetrics.query.filter_by(date=block.schedule.date).first()
    if old_metrics:
        old_metrics.tasks_rescheduled += 1
    
    db.session.delete(block)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Task rescheduled to {new_date}',
        'new_schedule': new_schedule.to_dict()
    })


# ============================================================================
# POMODORO TIMER
# ============================================================================

@api.route('/pomodoro/start/<int:block_id>', methods=['POST'])
def start_pomodoro(block_id):
    """Start a pomodoro session for a study block."""
    block = StudyBlock.query.get_or_404(block_id)
    
    # Create new pomodoro session
    session = PomodoroSession(
        study_block_id=block_id,
        start_time=datetime.utcnow(),
        status='in_progress',
        session_type='focus'
    )
    db.session.add(session)
    
    # Update block
    if not block.actual_start_time:
        block.actual_start_time = datetime.utcnow()
    block.pomodoro_sessions += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })


@api.route('/pomodoro/pause/<int:session_id>', methods=['POST'])
def pause_pomodoro(session_id):
    """Pause a pomodoro session."""
    session = PomodoroSession.query.get_or_404(session_id)
    session.status = 'paused'
    session.end_time = datetime.utcnow()
    
    if session.start_time:
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })


@api.route('/pomodoro/resume/<int:session_id>', methods=['POST'])
def resume_pomodoro(session_id):
    """Resume a paused pomodoro session."""
    session = PomodoroSession.query.get_or_404(session_id)
    
    # Create new session for the resumed work
    new_session = PomodoroSession(
        study_block_id=session.study_block_id,
        start_time=datetime.utcnow(),
        status='in_progress',
        session_type='focus'
    )
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session': new_session.to_dict()
    })


@api.route('/pomodoro/finish/<int:session_id>', methods=['POST'])
def finish_pomodoro(session_id):
    """Finish a pomodoro session."""
    session = PomodoroSession.query.get_or_404(session_id)
    session.status = 'completed'
    session.end_time = datetime.utcnow()
    
    if session.start_time:
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })


@api.route('/pomodoro/interrupt/<int:session_id>', methods=['POST'])
def interrupt_pomodoro(session_id):
    """Mark a pomodoro session as interrupted."""
    session = PomodoroSession.query.get_or_404(session_id)
    session.status = 'interrupted'
    session.end_time = datetime.utcnow()
    
    if session.start_time:
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    
    # Update block
    block = session.study_block
    block.interrupted += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })


# ============================================================================
# ANALYTICS
# ============================================================================

@api.route('/analytics/daily/<date>', methods=['GET'])
def get_daily_analytics(date):
    """Get analytics for a specific date."""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    metrics = DailyMetrics.query.filter_by(date=date_obj).first()
    schedule = DailySchedule.query.filter_by(date=date_obj).first()
    
    return jsonify({
        'date': date,
        'metrics': metrics.to_dict() if metrics else {},
        'schedule': schedule.to_dict() if schedule else None,
    })


@api.route('/analytics/weekly/<start_date>', methods=['GET'])
def get_weekly_analytics(start_date):
    """Get weekly analytics starting from a date."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    end = start + timedelta(days=6)
    
    metrics = DailyMetrics.query.filter(
        DailyMetrics.date >= start,
        DailyMetrics.date <= end
    ).all()
    
    # Calculate aggregates
    total_study_minutes = sum(m.total_study_minutes for m in metrics)
    total_xp = sum(m.xp_earned for m in metrics)
    tasks_completed = sum(m.tasks_completed for m in metrics)
    tasks_missed = sum(m.tasks_missed for m in metrics)
    
    # Subject breakdown
    subject_minutes = {}
    for m in metrics:
        import json
        subject_data = json.loads(m.subject_minutes or '{}')
        for subject, minutes in subject_data.items():
            subject_minutes[subject] = subject_minutes.get(subject, 0) + minutes
    
    return jsonify({
        'start_date': start_date,
        'end_date': end.isoformat(),
        'days_included': len(metrics),
        'total_study_minutes': total_study_minutes,
        'average_daily_minutes': total_study_minutes / len(metrics) if metrics else 0,
        'total_xp': total_xp,
        'tasks_completed': tasks_completed,
        'tasks_missed': tasks_missed,
        'subject_minutes': subject_minutes,
        'daily_metrics': [m.to_dict() for m in metrics],
    })


@api.route('/analytics/monthly/<year>/<month>', methods=['GET'])
def get_monthly_analytics(year, month):
    """Get monthly analytics."""
    try:
        year = int(year)
        month = int(month)
        start = datetime(year, month, 1).date()
        
        if month == 12:
            end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Invalid year/month'}), 400
    
    metrics = DailyMetrics.query.filter(
        DailyMetrics.date >= start,
        DailyMetrics.date <= end
    ).all()
    
    # Calculate aggregates
    total_study_minutes = sum(m.total_study_minutes for m in metrics)
    total_xp = sum(m.xp_earned for m in metrics)
    tasks_completed = sum(m.tasks_completed for m in metrics)
    
    # Heatmap data
    heatmap = {}
    for m in metrics:
        heatmap[m.date.isoformat()] = m.total_study_minutes
    
    return jsonify({
        'year': year,
        'month': month,
        'total_study_minutes': total_study_minutes,
        'average_daily_minutes': total_study_minutes / len(metrics) if metrics else 0,
        'total_xp': total_xp,
        'tasks_completed': tasks_completed,
        'heatmap': heatmap,
    })


@api.route('/analytics/streaks', methods=['GET'])
def get_streaks():
    """Get study streak information."""
    today = datetime.now().date()
    
    # Calculate current streak
    current_streak = 0
    check_date = today
    
    while True:
        metrics = DailyMetrics.query.filter_by(date=check_date).first()
        schedule = DailySchedule.query.filter_by(date=check_date).first()
        
        if metrics and metrics.total_study_minutes >= 60:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Calculate longest streak
    all_metrics = DailyMetrics.query.order_by(DailyMetrics.date).all()
    longest_streak = 0
    current_count = 0
    prev_date = None
    
    for m in all_metrics:
        if m.total_study_minutes >= 60:
            if prev_date and (m.date - prev_date).days == 1:
                current_count += 1
            else:
                current_count = 1
            longest_streak = max(longest_streak, current_count)
            prev_date = m.date
    
    return jsonify({
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'today_studied': DailyMetrics.query.filter_by(date=today).first() is not None,
    })


@api.route('/analytics/semester', methods=['GET'])
def get_semester_analytics():
    """Get semester-wide analytics."""
    start = datetime.strptime(get_config('start_date', '2025-07-14'), '%Y-%m-%d').date()
    end = datetime.strptime(get_config('end_date', '2025-11-10'), '%Y-%m-%d').date()
    
    metrics = DailyMetrics.query.filter(
        DailyMetrics.date >= start,
        DailyMetrics.date <= end
    ).all()
    
    total_study_hours = sum(m.total_study_minutes for m in metrics) / 60
    total_xp = sum(m.xp_earned for m in metrics)
    tasks_completed = sum(m.tasks_completed for m in metrics)
    tasks_missed = sum(m.tasks_missed for m in metrics)
    
    # Subject progress
    subject_progress = SubjectProgress.query.all()
    
    return jsonify({
        'period': f'{start} to {end}',
        'days_covered': len(metrics),
        'total_study_hours': round(total_study_hours, 1),
        'average_daily_hours': round(total_study_hours / len(metrics), 1) if metrics else 0,
        'total_xp': total_xp,
        'tasks_completed': tasks_completed,
        'tasks_missed': tasks_missed,
        'completion_rate': round(tasks_completed / (tasks_completed + tasks_missed) * 100, 1) 
                          if (tasks_completed + tasks_missed) > 0 else 0,
        'subject_progress': [sp.to_dict() for sp in subject_progress],
    })


# ============================================================================
# SUBJECT PROGRESS
# ============================================================================

@api.route('/subjects', methods=['GET'])
def get_subjects():
    """Get all subject progress."""
    subjects = SubjectProgress.query.all()
    return jsonify({
        'subjects': [s.to_dict() for s in subjects]
    })


@api.route('/subjects/<subject_name>', methods=['GET'])
def get_subject(subject_name):
    """Get progress for a specific subject."""
    subject = SubjectProgress.query.filter_by(subject_name=subject_name).first()
    
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404
    
    return jsonify(subject.to_dict())


@api.route('/subjects/<subject_name>/progress', methods=['POST'])
def update_subject_progress(subject_name):
    """Update progress for a subject."""
    data = request.get_json()
    
    subject = SubjectProgress.query.filter_by(subject_name=subject_name).first()
    
    if not subject:
        # Create new subject progress
        subject = SubjectProgress(subject_name=subject_name)
        db.session.add(subject)
    
    if 'completed_topics' in data:
        import json
        subject.completed_topics = json.dumps(data['completed_topics'])
    
    if 'confidence_scores' in data:
        import json
        subject.confidence_scores = json.dumps(data['confidence_scores'])
    
    if 'total_topics' in data:
        subject.total_topics = data['total_topics']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'subject': subject.to_dict()
    })


# ============================================================================
# DAILY METRICS
# ============================================================================

@api.route('/metrics/<date>', methods=['GET'])
def get_metrics(date):
    """Get daily metrics for a date."""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    metrics = DailyMetrics.query.filter_by(date=date_obj).first()
    
    if not metrics:
        metrics = DailyMetrics(date=date_obj)
        db.session.add(metrics)
        db.session.commit()
    
    return jsonify(metrics.to_dict())


@api.route('/metrics/<date>', methods=['PUT'])
def update_metrics(date):
    """Update daily metrics."""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    data = request.get_json()
    metrics = DailyMetrics.query.filter_by(date=date_obj).first()
    
    if not metrics:
        metrics = DailyMetrics(date=date_obj)
        db.session.add(metrics)
    
    # Update fields
    if 'mood_rating' in data:
        metrics.mood_rating = data['mood_rating']
    if 'energy_rating' in data:
        metrics.energy_rating = data['energy_rating']
    if 'notes' in data:
        metrics.notes = data['notes']
    if 'productive_minutes' in data:
        metrics.productive_minutes = data['productive_minutes']
    if 'distraction_minutes' in data:
        metrics.distraction_minutes = data['distraction_minutes']
    if 'subject_minutes' in data:
        import json
        metrics.subject_minutes = json.dumps(data['subject_minutes'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'metrics': metrics.to_dict()
    })


# ============================================================================
# MISSED TASKS
# ============================================================================

@api.route('/missed-tasks', methods=['GET'])
def get_missed_tasks():
    """Get all missed tasks."""
    tasks = MissedTask.query.filter_by(rescheduled=False).order_by(MissedTask.original_date).all()
    return jsonify({
        'tasks': [t.to_dict() for t in tasks]
    })


# ============================================================================
# CALENDAR
# ============================================================================

@api.route('/calendar', methods=['GET'])
def get_calendar():
    """Get calendar data for a month."""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Get all schedules for the month
    start = datetime(year, month, 1).date()
    if month == 12:
        end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    schedules = DailySchedule.query.filter(
        DailySchedule.date >= start,
        DailySchedule.date <= end
    ).all()
    
    # Get metrics for completion status
    metrics = DailyMetrics.query.filter(
        DailyMetrics.date >= start,
        DailyMetrics.date <= end
    ).all()
    metrics_dict = {m.date: m for m in metrics}
    
    calendar_data = []
    today = datetime.now().date()
    
    for schedule in schedules:
        schedule_date = schedule.date
        
        # Determine status
        if schedule_date == today:
            status = 'current'
        elif schedule_date > today:
            status = 'future'
        elif schedule_date in metrics_dict:
            m = metrics_dict[schedule_date]
            if m.tasks_completed > 0 and m.tasks_missed == 0:
                status = 'completed'
            elif m.tasks_completed > 0 or m.tasks_missed > 0:
                status = 'partial'
            else:
                status = 'pending'
        else:
            status = 'pending'
        
        calendar_data.append({
            'date': schedule_date.isoformat(),
            'status': status,
            'mode': schedule.mode,
            'completion_percentage': schedule.completion_percentage,
            'total_study_minutes': schedule.total_study_minutes,
        })
    
    return jsonify({
        'year': year,
        'month': month,
        'days': calendar_data
    })


# ============================================================================
# CONFIGURATION
# ============================================================================

@api.route('/config', methods=['GET'])
def get_all_config():
    """Get all configuration."""
    configs = Configuration.query.all()
    return jsonify({
        'config': {c.key: c.value for c in configs}
    })


@api.route('/config/<key>', methods=['GET'])
def get_config_value(key):
    """Get a specific configuration value."""
    value = get_config(key)
    return jsonify({'key': key, 'value': value})


@api.route('/config/<key>', methods=['PUT'])
def update_config(key):
    """Update a configuration value."""
    data = request.get_json()
    value = data.get('value')
    
    if value is None:
        return jsonify({'error': 'Value is required'}), 400
    
    set_config(key, value)
    
    return jsonify({
        'success': True,
        'key': key,
        'value': value
    })


# ============================================================================
# REGENERATE TIMETABLE
# ============================================================================

@api.route('/regenerate', methods=['POST'])
def regenerate_timetable():
    """Regenerate timetable with new constraints."""
    data = request.get_json() or {}
    
    # Update constraints if provided
    if 'start_date' in data:
        set_config('start_date', data['start_date'])
    if 'end_date' in data:
        set_config('end_date', data['end_date'])
    if 'amcat_start_date' in data:
        set_config('amcat_start_date', data['amcat_start_date'])
    if 'amcat_end_date' in data:
        set_config('amcat_end_date', data['amcat_end_date'])
    if 'exam_start_date' in data:
        set_config('exam_start_date', data['exam_start_date'])
    
    # Regenerate
    return generate_timetable()