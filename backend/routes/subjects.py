"""
Subjects routes - Subject management and progress.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

from database import get_db
from models.database import User, Subject, SubjectProgress
from utils.security import get_current_user

router = APIRouter()


class SubjectProgressUpdate(BaseModel):
    completed_topics: Optional[List[str]] = None
    confidence_scores: Optional[dict] = None
    total_topics: Optional[int] = None


@router.get("/")
def get_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subjects with progress."""
    # Get subject definitions
    subjects = db.query(Subject).all()
    
    # Get user progress
    progress_list = db.query(SubjectProgress).filter(
        SubjectProgress.user_id == current_user.id
    ).all()
    
    progress_dict = {p.subject_name: p for p in progress_list}
    
    result = []
    for subj in subjects:
        topics = json.loads(subj.topics or "[]")
        progress = progress_dict.get(subj.name)
        
        if progress:
            completed = json.loads(progress.completed_topics or "[]")
            confidence = json.loads(progress.confidence_scores or "{}")
            weak = json.loads(progress.weak_topics or "[]")
        else:
            completed = []
            confidence = {}
            weak = []
        
        result.append({
            "id": subj.id,
            "name": subj.name,
            "priority": subj.priority,
            "difficulty": subj.difficulty,
            "placement_importance": subj.placement_importance,
            "target_hours_min": subj.target_hours_min,
            "target_hours_max": subj.target_hours_max,
            "topics": topics,
            "topics_count": len(topics),
            "completed_topics": completed,
            "confidence_scores": confidence,
            "weak_topics": weak,
            "completion_percentage": (len(completed) / len(topics) * 100) if topics else 0,
            "total_study_hours": progress.total_study_hours if progress else 0,
            "revision_count": progress.revision_count if progress else 0,
            "last_studied": progress.last_studied.isoformat() if progress and progress.last_studied else None,
        })
    
    return {"subjects": result}


@router.get("/{subject_name}")
def get_subject(
    subject_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific subject with detailed progress."""
    subject = db.query(Subject).filter(Subject.name == subject_name).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    progress = db.query(SubjectProgress).filter(
        SubjectProgress.user_id == current_user.id,
        SubjectProgress.subject_name == subject_name
    ).first()
    
    topics = json.loads(subject.topics or "[]")
    
    if progress:
        completed = json.loads(progress.completed_topics or "[]")
        confidence = json.loads(progress.confidence_scores or "{}")
        weak = json.loads(progress.weak_topics or "[]")
    else:
        completed = []
        confidence = {}
        weak = []
    
    return {
        "id": subject.id,
        "name": subject.name,
        "priority": subject.priority,
        "difficulty": subject.difficulty,
        "placement_importance": subject.placement_importance,
        "target_hours_min": subject.target_hours_min,
        "target_hours_max": subject.target_hours_max,
        "topics": topics,
        "completed_topics": completed,
        "confidence_scores": confidence,
        "weak_topics": weak,
        "completion_percentage": (len(completed) / len(topics) * 100) if topics else 0,
        "total_study_hours": progress.total_study_hours if progress else 0,
        "revision_count": progress.revision_count if progress else 0,
        "last_studied": progress.last_studied.isoformat() if progress and progress.last_studied else None,
    }


@router.put("/{subject_name}/progress")
def update_subject_progress(
    subject_name: str,
    update: SubjectProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress for a subject."""
    subject = db.query(Subject).filter(Subject.name == subject_name).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    progress = db.query(SubjectProgress).filter(
        SubjectProgress.user_id == current_user.id,
        SubjectProgress.subject_name == subject_name
    ).first()
    
    if not progress:
        progress = SubjectProgress(
            user_id=current_user.id,
            subject_name=subject_name,
            total_topics=len(json.loads(subject.topics or "[]"))
        )
        db.add(progress)
    
    if update.completed_topics is not None:
        progress.completed_topics = json.dumps(update.completed_topics)
        progress.last_studied = datetime.now().date()
    
    if update.confidence_scores is not None:
        progress.confidence_scores = json.dumps(update.confidence_scores)
        # Update weak topics
        weak = [t for t, c in update.confidence_scores.items() if c < 0.6]
        progress.weak_topics = json.dumps(weak)
    
    if update.total_topics is not None:
        progress.total_topics = update.total_topics
    
    db.commit()
    db.refresh(progress)
    
    return {
        "success": True,
        "progress": progress.to_dict()
    }


@router.post("/{subject_name}/topic/{topic}/complete")
def complete_topic(
    subject_name: str,
    topic: str,
    confidence: float = 0.7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a topic as completed."""
    progress = db.query(SubjectProgress).filter(
        SubjectProgress.user_id == current_user.id,
        SubjectProgress.subject_name == subject_name
    ).first()
    
    if not progress:
        subject = db.query(Subject).filter(Subject.name == subject_name).first()
        progress = SubjectProgress(
            user_id=current_user.id,
            subject_name=subject_name,
            total_topics=len(json.loads(subject.topics or "[]")) if subject else 0
        )
        db.add(progress)
    
    completed = json.loads(progress.completed_topics or "[]")
    if topic not in completed:
        completed.append(topic)
        progress.completed_topics = json.dumps(completed)
    
    confidence_scores = json.loads(progress.confidence_scores or "{}")
    confidence_scores[topic] = confidence
    progress.confidence_scores = json.dumps(confidence_scores)
    
    # Update weak topics
    weak = [t for t, c in confidence_scores.items() if c < 0.6]
    progress.weak_topics = json.dumps(weak)
    
    progress.last_studied = datetime.now().date()
    progress.revision_count += 1
    
    # Award XP
    from services.gamification import GamificationService, XP_REWARDS
    gamification = GamificationService(db, current_user.id)
    gamification.add_xp(XP_REWARDS["topic_complete"], f"Completed {topic}")
    
    db.commit()
    
    return {
        "success": True,
        "completed_topics": completed,
        "completion_percentage": (len(completed) / progress.total_topics * 100) if progress.total_topics > 0 else 0,
    }


@router.get("/{subject_name}/weak-topics")
def get_weak_topics(
    subject_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weak topics for a subject."""
    progress = db.query(SubjectProgress).filter(
        SubjectProgress.user_id == current_user.id,
        SubjectProgress.subject_name == subject_name
    ).first()
    
    if not progress:
        return {"weak_topics": []}
    
    weak = json.loads(progress.weak_topics or "[]")
    confidence_scores = json.loads(progress.confidence_scores or "{}")
    
    result = []
    for topic in weak:
        result.append({
            "topic": topic,
            "confidence": confidence_scores.get(topic, 0),
        })
    
    return {"weak_topics": sorted(result, key=lambda x: x["confidence"])}
