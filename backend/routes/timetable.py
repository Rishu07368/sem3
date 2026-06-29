"""
Timetable routes - Schedule generation and management.
"""
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models.database import User, DailySchedule, FixedTimeSlot, StudyBlock, Configuration
from utils.security import get_current_user
from services.scheduling_engine import SchedulingEngine, SchedulingConstraints, StudyMode, TimeSlot, StudyBlock as SB
from services.subjects import get_default_subjects

router = APIRouter()


def get_constraints(db: Session) -> SchedulingConstraints:
    """Get scheduling constraints from configuration."""
    def get_config(key: str, default: str) -> str:
        config = db.query(Configuration).filter(Configuration.key == key).first()
        return config.value if config else default
    
    start_date = datetime.strptime(get_config('start_date', '2025-07-14'), '%Y-%m-%d')
    end_date = datetime.strptime(get_config('end_date', '2025-11-10'), '%Y-%m-%d')
    amcat_start_str = get_config('amcat_start_date', '2025-08-15')
    amcat_end_str = get_config('amcat_end_date', '2025-09-15')
    
    amcat_start = datetime.strptime(amcat_start_str, '%Y-%m-%d').date() if amcat_start_str else None
    amcat_end = datetime.strptime(amcat_end_str, '%Y-%m-%d').date() if amcat_end_str else None
    
    return SchedulingConstraints(
        start_date=start_date,
        end_date=end_date,
        amcat_start_date=amcat_start,
        amcat_end_date=amcat_end,
    )


def create_engine(db: Session) -> SchedulingEngine:
    """Create a scheduling engine with subjects."""
    engine = SchedulingEngine(get_constraints(db))
    for subject in get_default_subjects():
        engine.add_subject(subject)
    return engine


@router.post("/generate")
def generate_timetable(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate complete timetable for the semester."""
    engine = create_engine(db)
    schedules = engine.generate_timetable()
    
    generated_count = 0
    
    for schedule in schedules:
        existing = db.query(DailySchedule).filter(
            DailySchedule.user_id == current_user.id,
            DailySchedule.date == schedule.date.date()
        ).first()
        
        if existing:
            existing.mode = schedule.mode.value
            existing.total_study_minutes = schedule.total_study_minutes
        else:
            daily_schedule = DailySchedule(
                user_id=current_user.id,
                date=schedule.date.date(),
                mode=schedule.mode.value,
                total_study_minutes=schedule.total_study_minutes,
            )
            db.add(daily_schedule)
            db.flush()
            
            # Add fixed slots
            for slot in schedule.time_slots:
                fixed_slot = FixedTimeSlot(
                    schedule_id=daily_schedule.id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    activity=slot.activity,
                    flexible_end=slot.flexible_end
                )
                db.add(fixed_slot)
            
            # Add study blocks
            for idx, block in enumerate(schedule.study_blocks):
                study_block = StudyBlock(
                    user_id=current_user.id,
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
                db.add(study_block)
            
            generated_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Generated {generated_count} new daily schedules",
        "total_schedules": db.query(DailySchedule).filter(
            DailySchedule.user_id == current_user.id
        ).count()
    }


@router.get("/schedule/{date_str}")
def get_schedule(
    date_str: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedule for a specific date."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    schedule = db.query(DailySchedule).filter(
        DailySchedule.user_id == current_user.id,
        DailySchedule.date == date_obj
    ).first()
    
    if not schedule:
        # Generate schedule for this date
        engine = create_engine(db)
        schedule_data = engine.generate_daily_schedule(
            datetime.combine(date_obj, datetime.min.time())
        )
        
        daily_schedule = DailySchedule(
            user_id=current_user.id,
            date=date_obj,
            mode=schedule_data.mode.value,
            total_study_minutes=schedule_data.total_study_minutes,
        )
        db.add(daily_schedule)
        db.flush()
        
        for slot in schedule_data.time_slots:
            fixed_slot = FixedTimeSlot(
                schedule_id=daily_schedule.id,
                start_time=slot.start_time,
                end_time=slot.end_time,
                activity=slot.activity,
                flexible_end=slot.flexible_end
            )
            db.add(fixed_slot)
        
        for idx, block in enumerate(schedule_data.study_blocks):
            study_block = StudyBlock(
                user_id=current_user.id,
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
            db.add(study_block)
        
        db.commit()
        return daily_schedule.to_dict()
    
    return schedule.to_dict()


@router.get("/schedules")
def get_schedules(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedules within a date range."""
    query = db.query(DailySchedule).filter(
        DailySchedule.user_id == current_user.id
    )
    
    if start:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        query = query.filter(DailySchedule.date >= start_date)
    
    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        query = query.filter(DailySchedule.date <= end_date)
    
    schedules = query.order_by(DailySchedule.date).all()
    
    return {
        "schedules": [s.to_dict() for s in schedules],
        "count": len(schedules)
    }


@router.get("/blocks/{block_id}")
def get_block(
    block_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific study block."""
    block = db.query(StudyBlock).filter(
        StudyBlock.id == block_id,
        StudyBlock.user_id == current_user.id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    return block.to_dict()


@router.post("/blocks/{block_id}/complete")
def complete_block(
    block_id: int,
    actual_duration: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a study block as completed."""
    block = db.query(StudyBlock).filter(
        StudyBlock.id == block_id,
        StudyBlock.user_id == current_user.id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    block.completed = True
    block.actual_start_time = datetime.now()
    block.actual_end_time = datetime.now()
    block.actual_duration_minutes = actual_duration or block.duration_minutes
    
    # Calculate XP
    from services.gamification import GamificationService
    gamification = GamificationService(db, current_user.id)
    xp_result = gamification.award_xp_for_block_complete(block)
    block.xp_earned = xp_result["xp_added"]
    
    db.commit()
    
    return {
        "success": True,
        "xp_earned": xp_result["xp_added"],
        "total_xp": xp_result["total_xp"],
        "leveled_up": xp_result["leveled_up"],
    }


@router.post("/blocks/{block_id}/miss")
def miss_block(
    block_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a study block as missed."""
    block = db.query(StudyBlock).filter(
        StudyBlock.id == block_id,
        StudyBlock.user_id == current_user.id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    # Create missed task
    schedule = db.query(DailySchedule).filter(
        DailySchedule.id == block.schedule_id
    ).first()
    
    missed_task = MissedTask(
        user_id=current_user.id,
        original_date=schedule.date if schedule else datetime.now().date(),
        subject=block.subject,
        topic=block.topic,
    )
    db.add(missed_task)
    
    # Deduct XP
    from services.gamification import GamificationService, XP_REWARDS
    gamification = GamificationService(db, current_user.id)
    gamification.add_xp(XP_REWARDS["task_missed"], "Missed task")
    
    db.commit()
    
    return {"success": True, "message": "Task marked as missed"}
