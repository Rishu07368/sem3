"""
Revision Engine
Implements spaced repetition for optimal learning retention.
"""
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json

from sqlalchemy.orm import Session

from models.database import RevisionSession, SubjectProgress, StudyBlock


# Spaced repetition intervals (in days)
REVISION_INTERVALS = [1, 3, 7, 14, 30, 60, 90]


class RevisionEngine:
    """
    Implements spaced repetition for study topics.
    
    Based on the SuperMemo SM-2 algorithm with simplified intervals.
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def schedule_revision(
        self,
        subject: str,
        topic: str,
        study_block_id: Optional[int] = None,
        confidence: float = 0.5
    ) -> RevisionSession:
        """
        Schedule a new revision session for a topic.
        
        Args:
            subject: Subject name
            topic: Topic name
            study_block_id: Associated study block ID (optional)
            confidence: Initial confidence level (0-1)
        
        Returns:
            Created RevisionSession
        """
        today = datetime.now().date()
        
        revision = RevisionSession(
            user_id=self.user_id,
            study_block_id=study_block_id,
            subject=subject,
            topic=topic,
            interval=1,  # First revision after 1 day
            next_revision_date=today + timedelta(days=1),
            repetitions=0,
            ease_factor=2.5,
            last_reviewed=today,
            confidence=confidence
        )
        
        self.db.add(revision)
        self.db.commit()
        self.db.refresh(revision)
        
        return revision
    
    def get_due_revisions(self, target_date: Optional[date] = None) -> List[RevisionSession]:
        """
        Get all revision sessions due for review.
        
        Args:
            target_date: Date to check for due revisions (default: today)
        
        Returns:
            List of due RevisionSession objects
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        due_revisions = self.db.query(RevisionSession).filter(
            RevisionSession.user_id == self.user_id,
            RevisionSession.next_revision_date <= target_date,
            RevisionSession.confidence < 1.0  # Skip if mastered
        ).all()
        
        return due_revisions
    
    def get_revisions_by_subject(self, subject: str) -> List[RevisionSession]:
        """Get all revision sessions for a specific subject."""
        return self.db.query(RevisionSession).filter(
            RevisionSession.user_id == self.user_id,
            RevisionSession.subject == subject
        ).all()
    
    def complete_revision(
        self,
        revision_id: int,
        quality: int  # 0-5 rating (0=forgot, 5=perfect)
    ) -> RevisionSession:
        """
        Complete a revision session and update the schedule.
        
        Args:
            revision_id: ID of the revision session
            quality: Quality of recall (0-5)
                0 = Complete blackout
                1 = Incorrect, but remembered upon seeing answer
                2 = Incorrect, but answer seemed easy to recall
                3 = Correct with serious difficulty
                4 = Correct with some hesitation
                5 = Perfect recall
        
        Returns:
            Updated RevisionSession with new interval
        """
        revision = self.db.query(RevisionSession).filter(
            RevisionSession.id == revision_id,
            RevisionSession.user_id == self.user_id
        ).first()
        
        if not revision:
            raise ValueError(f"Revision session {revision_id} not found")
        
        today = datetime.now().date()
        
        # Update based on SM-2 algorithm
        revision.repetitions += 1
        revision.last_reviewed = today
        
        # Calculate new confidence
        revision.confidence = min(1.0, revision.confidence + (quality / 5.0) * 0.2)
        
        if quality >= 3:
            # Successful recall - increase interval
            if revision.repetitions == 1:
                revision.interval = 1
            elif revision.repetitions == 2:
                revision.interval = 3
            else:
                revision.interval = int(revision.interval * revision.ease_factor)
            
            # Update ease factor
            revision.ease_factor = max(1.3, revision.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        else:
            # Failed recall - reset
            revision.repetitions = 0
            revision.interval = 1
        
        # Cap interval at 90 days
        revision.interval = min(revision.interval, 90)
        
        # Schedule next revision
        revision.next_revision_date = today + timedelta(days=revision.interval)
        
        self.db.commit()
        self.db.refresh(revision)
        
        return revision
    
    def skip_revision(self, revision_id: int) -> RevisionSession:
        """
        Skip a revision (will reschedule for tomorrow).
        
        Args:
            revision_id: ID of the revision session
        
        Returns:
            Updated RevisionSession
        """
        revision = self.db.query(RevisionSession).filter(
            RevisionSession.id == revision_id,
            RevisionSession.user_id == self.user_id
        ).first()
        
        if not revision:
            raise ValueError(f"Revision session {revision_id} not found")
        
        revision.next_revision_date = datetime.now().date() + timedelta(days=1)
        
        self.db.commit()
        self.db.refresh(revision)
        
        return revision
    
    def delete_revision(self, revision_id: int) -> bool:
        """
        Delete a revision session.
        
        Args:
            revision_id: ID of the revision session
        
        Returns:
            True if deleted
        """
        revision = self.db.query(RevisionSession).filter(
            RevisionSession.id == revision_id,
            RevisionSession.user_id == self.user_id
        ).first()
        
        if revision:
            self.db.delete(revision)
            self.db.commit()
            return True
        
        return False
    
    def get_revision_stats(self) -> Dict:
        """Get revision statistics for the user."""
        all_revisions = self.db.query(RevisionSession).filter(
            RevisionSession.user_id == self.user_id
        ).all()
        
        total = len(all_revisions)
        mastered = len([r for r in all_revisions if r.confidence >= 0.9])
        learning = len([r for r in all_revisions if 0.5 <= r.confidence < 0.9])
        weak = len([r for r in all_revisions if r.confidence < 0.5])
        
        today = datetime.now().date()
        due_today = len([r for r in all_revisions if r.next_revision_date <= today])
        
        return {
            "total_topics": total,
            "mastered": mastered,
            "learning": learning,
            "weak": weak,
            "due_today": due_today,
            "mastery_percentage": (mastered / total * 100) if total > 0 else 0,
        }
    
    def get_weak_topics(self, subject: Optional[str] = None) -> List[Dict]:
        """
        Get topics with lowest confidence scores.
        
        Args:
            subject: Filter by subject (optional)
        
        Returns:
            List of topics with confidence < 0.6
        """
        query = self.db.query(RevisionSession).filter(
            RevisionSession.user_id == self.user_id,
            RevisionSession.confidence < 0.6
        )
        
        if subject:
            query = query.filter(RevisionSession.subject == subject)
        
        revisions = query.order_by(RevisionSession.confidence).all()
        
        return [
            {
                "id": r.id,
                "subject": r.subject,
                "topic": r.topic,
                "confidence": r.confidence,
                "interval": r.interval,
                "next_revision": r.next_revision_date.isoformat(),
            }
            for r in revisions
        ]
    
    def auto_schedule_from_study_block(
        self,
        study_block: StudyBlock,
        confidence: float = 0.5
    ) -> List[RevisionSession]:
        """
        Automatically schedule revision sessions after completing a study block.
        
        Args:
            study_block: The completed study block
            confidence: Initial confidence level
        
        Returns:
            List of created revision sessions
        """
        sessions = []
        
        # Schedule initial revision
        session = self.schedule_revision(
            subject=study_block.subject,
            topic=study_block.topic,
            study_block_id=study_block.id,
            confidence=confidence
        )
        sessions.append(session)
        
        # Pre-schedule future revisions based on intervals
        for interval in REVISION_INTERVALS[1:5]:  # Schedule up to 30 days
            future_date = datetime.now().date() + timedelta(days=interval)
            
            future_session = RevisionSession(
                user_id=self.user_id,
                study_block_id=study_block.id,
                subject=study_block.subject,
                topic=study_block.topic,
                interval=interval,
                next_revision_date=future_date,
                repetitions=0,
                ease_factor=2.5,
                confidence=0.5
            )
            self.db.add(future_session)
            sessions.append(future_session)
        
        self.db.commit()
        
        return sessions
