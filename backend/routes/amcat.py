"""
AMCAT routes - AMCAT preparation tracking and management.
"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

from database import get_db
from models.database import User, StudyBlock, SubjectProgress
from utils.security import get_current_user
from services.analytics_engine import AnalyticsEngine

router = APIRouter()


class AMCATSection(BaseModel):
    name: str
    topics: List[str]
    hours_target: float
    hours_completed: float
    practice_tests: int
    average_score: float


@router.get("/")
def get_amcat_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AMCAT preparation overview."""
    amcat_start = date(2025, 8, 15)
    amcat_end = date(2025, 9, 15)
    today = datetime.now().date()
    
    # Determine if we're in AMCAT period
    in_amcat_period = amcat_start <= today <= amcat_end
    days_until_amcat = max(0, (amcat_start - today).days)
    
    # Get AMCAT study blocks
    amcat_blocks = db.query(StudyBlock).filter(
        StudyBlock.user_id == current_user.id,
        StudyBlock.is_amcat == True
    ).all()
    
    completed = [b for b in amcat_blocks if b.completed]
    
    # Calculate readiness
    analytics = AnalyticsEngine(db, current_user.id)
    readiness = analytics.get_amcat_readiness()
    
    return {
        "in_amcat_period": in_amcat_period,
        "amcat_start": amcat_start.isoformat(),
        "amcat_end": amcat_end.isoformat(),
        "days_until_amcat": days_until_amcat,
        "total_blocks": len(amcat_blocks),
        "completed_blocks": len(completed),
        "completion_percentage": (len(completed) / len(amcat_blocks) * 100) if amcat_blocks else 0,
        "readiness": readiness,
    }


@router.get("/sections")
def get_amcat_sections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AMCAT sections with progress."""
    sections = [
        {
            "id": "quants",
            "name": "Quantitative Aptitude",
            "topics": [
                "Number Systems", "Progressions", "Percentages", "Profit and Loss",
                "Time and Work", "Time Speed Distance", "Ratio Proportion",
                "Averages", "Mixtures", "Quadratic Equations", "SI CI",
                "Permutation Combination", "Probability"
            ],
            "hours_target": 20,
            "icon": "calculator",
        },
        {
            "id": "logical",
            "name": "Logical Reasoning",
            "topics": [
                "Blood Relations", "Coding Decoding", "Direction Sense",
                "Seating Arrangement", "Syllogism", "Analogies",
                "Series Completion", "Data Sufficiency", "Puzzles",
                "Statement Conclusion"
            ],
            "hours_target": 15,
            "icon": "brain",
        },
        {
            "id": "english",
            "name": "English",
            "topics": [
                "Reading Comprehension", "Grammar", "Vocabulary",
                "Synonyms Antonyms", "Sentence Completion", "Error Spotting",
                "Para Jumbles", "Fill in Blanks"
            ],
            "hours_target": 10,
            "icon": "book",
        },
        {
            "id": "coding",
            "name": "Coding",
            "topics": [
                "Array Problems", "String Problems", "Linked List",
                "Tree Problems", "Dynamic Programming", "Sorting Searching",
                "Graph Problems", "Recursion"
            ],
            "hours_target": 15,
            "icon": "code",
        },
        {
            "id": "debugging",
            "name": "Debugging",
            "topics": [
                "C Debugging", "C++ Debugging", "Java Debugging",
                "Python Debugging", "Error Identification", "Code Correction"
            ],
            "hours_target": 8,
            "icon": "bug",
        },
        {
            "id": "core_cs",
            "name": "Core CS",
            "topics": [
                "ADSA Fundamentals", "DBMS Queries", "Operating Systems",
                "Computer Networks", "COA Concepts"
            ],
            "hours_target": 5,
            "icon": "cpu",
        },
    ]
    
    # Get progress for each section
    for section in sections:
        section_name = section["name"]
        progress = db.query(SubjectProgress).filter(
            SubjectProgress.user_id == current_user.id,
            SubjectProgress.subject_name == section_name
        ).first()
        
        if progress:
            completed = json.loads(progress.completed_topics or "[]")
            section["topics_completed"] = len(completed)
            section["topics_total"] = len(section["topics"])
            section["hours_completed"] = progress.total_study_hours
            section["percentage"] = (len(completed) / len(section["topics"]) * 100) if section["topics"] else 0
        else:
            section["topics_completed"] = 0
            section["topics_total"] = len(section["topics"])
            section["hours_completed"] = 0
            section["percentage"] = 0
    
    return {"sections": sections}


@router.get("/readiness")
def get_amcat_readiness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed AMCAT readiness assessment."""
    analytics = AnalyticsEngine(db, current_user.id)
    return analytics.get_amcat_readiness()


@router.get("/schedule")
def get_amcat_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AMCAT-specific study schedule."""
    amcat_start = date(2025, 8, 15)
    today = datetime.now().date()
    
    # Generate AMCAT schedule for remaining days
    remaining_days = (amcat_end if (amcat_end := date(2025, 9, 15)) >= today else today)
    days_to_schedule = max(0, (amcat_end - today).days)
    
    schedule = []
    sections = [
        {"name": "Quantitative Aptitude", "hours_per_day": 2},
        {"name": "Logical Reasoning", "hours_per_day": 1.5},
        {"name": "English", "hours_per_day": 1},
        {"name": "Coding", "hours_per_day": 2},
        {"name": "Debugging", "hours_per_day": 1},
        {"name": "Core CS", "hours_per_day": 0.5},
    ]
    
    for i in range(min(days_to_schedule, 30)):  # Show 30 days max
        day = today + datetime.timedelta(days=i)
        day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day.weekday()]
        
        # Rotate focus areas
        primary = sections[i % len(sections)]
        secondary = sections[(i + 1) % len(sections)]
        
        schedule.append({
            "date": day.isoformat(),
            "day": day_name,
            "primary": primary["name"],
            "primary_hours": primary["hours_per_day"],
            "secondary": secondary["name"],
            "secondary_hours": secondary["hours_per_day"],
        })
    
    return {
        "days_remaining": days_to_schedule,
        "schedule": schedule,
    }


@router.post("/practice-test")
def log_practice_test(
    section: str,
    score: float,
    total: float = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a practice test result."""
    from services.gamification import GamificationService, XP_REWARDS
    
    percentage = (score / total) * 100
    
    # Award XP based on score
    xp = int(50 + (percentage / 10))
    
    gamification = GamificationService(db, current_user.id)
    gamification.add_xp(xp, f"AMCAT Practice Test: {section}")
    
    return {
        "success": True,
        "score": score,
        "total": total,
        "percentage": percentage,
        "xp_earned": xp,
    }
