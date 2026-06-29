"""
Tasks routes - Task management including missed tasks and pomodoro.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models.database import User, StudyBlock, MissedTask, PomodoroSession, DailyMetrics
from utils.security import get_current_user

router = APIRouter()


# Pomodoro settings
POMODORO_FOCUS_MINUTES = 25
POMODORO_SHORT_BREAK = 5
POMODORO_LONG_BREAK = 15


@router.get("/missed")
def get_missed_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all missed tasks."""
    tasks = db.query(MissedTask).filter(
        MissedTask.user_id == current_user.id,
        MissedTask.rescheduled == False
    ).order_by(MissedTask.original_date).all()
    
    return {"tasks": [t.to_dict() for t in tasks]}


@router.post("/missed/{task_id}/reschedule")
def reschedule_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reschedule a missed task."""
    task = db.query(MissedTask).filter(
        MissedTask.id == task_id,
        MissedTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.rescheduled = True
    task.rescheduled_to = datetime.now().date()
    
    db.commit()
    
    return {"success": True, "message": "Task rescheduled"}


@router.delete("/missed/{task_id}")
def delete_missed_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a missed task."""
    task = db.query(MissedTask).filter(
        MissedTask.id == task_id,
        MissedTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"success": True}


# Pomodoro Routes
@router.post("/pomodoro/start/{block_id}")
def start_pomodoro(
    block_id: int,
    session_type: str = "focus",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a pomodoro session."""
    block = db.query(StudyBlock).filter(
        StudyBlock.id == block_id,
        StudyBlock.user_id == current_user.id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    # Check for existing active session
    active = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.status == "in_progress"
    ).first()
    
    if active:
        raise HTTPException(status_code=400, detail="A pomodoro session is already in progress")
    
    session = PomodoroSession(
        user_id=current_user.id,
        study_block_id=block_id,
        start_time=datetime.now(),
        status="in_progress",
        session_type=session_type
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "start_time": session.start_time.isoformat(),
        "session_type": session_type,
    }


@router.post("/pomodoro/pause/{session_id}")
def pause_pomodoro(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause a pomodoro session."""
    session = db.query(PomodoroSession).filter(
        PomodoroSession.id == session_id,
        PomodoroSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not in progress")
    
    session.status = "paused"
    db.commit()
    
    return {"success": True, "status": "paused"}


@router.post("/pomodoro/resume/{session_id}")
def resume_pomodoro(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resume a paused pomodoro session."""
    session = db.query(PomodoroSession).filter(
        PomodoroSession.id == session_id,
        PomodoroSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != "paused":
        raise HTTPException(status_code=400, detail="Session is not paused")
    
    session.status = "in_progress"
    db.commit()
    
    return {"success": True, "status": "in_progress"}


@router.post("/pomodoro/finish/{session_id}")
def finish_pomodoro(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Finish a pomodoro session."""
    session = db.query(PomodoroSession).filter(
        PomodoroSession.id == session_id,
        PomodoroSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.end_time = datetime.now()
    session.status = "completed"
    
    if session.start_time and session.end_time:
        duration = (session.end_time - session.start_time).total_seconds() / 60
        session.duration_minutes = int(duration)
    
    # Update study block pomodoro count
    if session.study_block_id:
        block = db.query(StudyBlock).filter(StudyBlock.id == session.study_block_id).first()
        if block:
            block.pomodoro_sessions += 1
    
    # Award XP
    from services.gamification import GamificationService
    gamification = GamificationService(db, current_user.id)
    xp_result = gamification.award_xp_for_pomodoro(session.duration_minutes or 25, completed=True)
    session.xp_earned = xp_result["xp_added"]
    
    db.commit()
    
    return {
        "success": True,
        "duration_minutes": session.duration_minutes,
        "xp_earned": xp_result["xp_added"],
    }


@router.post("/pomodoro/interrupt/{session_id}")
def interrupt_pomodoro(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Interrupt a pomodoro session."""
    session = db.query(PomodoroSession).filter(
        PomodoroSession.id == session_id,
        PomodoroSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.end_time = datetime.now()
    session.status = "interrupted"
    
    if session.start_time and session.end_time:
        duration = (session.end_time - session.start_time).total_seconds() / 60
        session.duration_minutes = int(duration)
    
    # Update study block interrupted count
    if session.study_block_id:
        block = db.query(StudyBlock).filter(StudyBlock.id == session.study_block_id).first()
        if block:
            block.interrupted += 1
    
    # Deduct XP for interruption
    from services.gamification import GamificationService
    gamification = GamificationService(db, current_user.id)
    xp_result = gamification.award_xp_for_pomodoro(0, completed=False)
    
    db.commit()
    
    return {
        "success": True,
        "xp_lost": abs(xp_result["xp_added"]),
    }


@router.get("/pomodoro/active")
def get_active_pomodoro(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current active pomodoro session."""
    session = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.status.in_(["in_progress", "paused"])
    ).first()
    
    if not session:
        return {"active": False}
    
    return {
        "active": True,
        "session": session.to_dict()
    }


@router.get("/pomodoro/stats")
def get_pomodoro_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pomodoro statistics."""
    sessions = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.status == "completed"
    ).all()
    
    total_sessions = len(sessions)
    total_minutes = sum(s.duration_minutes for s in sessions if s.duration_minutes)
    
    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "total_hours": total_minutes / 60,
    }
