"""
Notification Service
Handles user notifications and reminders.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from models.database import Notification, User


class NotificationService:
    """
    Manages user notifications for reminders and alerts.
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info"
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=self.user_id,
            title=title,
            message=message,
            notification_type=notification_type,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_notifications(
        self,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for the user."""
        query = self.db.query(Notification).filter(
            Notification.user_id == self.user_id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == self.user_id
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self) -> int:
        """Mark all notifications as read."""
        count = self.db.query(Notification).filter(
            Notification.user_id == self.user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == self.user_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        return self.db.query(Notification).filter(
            Notification.user_id == self.user_id,
            Notification.is_read == False
        ).count()
    
    def notify_study_reminder(self, subject: str, topic: str) -> Notification:
        """Send a study reminder notification."""
        return self.create_notification(
            title="📚 Time to Study!",
            message=f"It's time to study {subject}: {topic}",
            notification_type="reminder"
        )
    
    def notify_revision_due(self, subject: str, topic: str) -> Notification:
        """Notify about due revision."""
        return self.create_notification(
            title="🔄 Revision Due",
            message=f"Time to revise {subject}: {topic}",
            notification_type="revision"
        )
    
    def notify_achievement_earned(self, achievement_name: str, xp: int) -> Notification:
        """Notify about earned achievement."""
        return self.create_notification(
            title="🏆 Achievement Unlocked!",
            message=f"You earned '{achievement_name}'! +{xp} XP",
            notification_type="achievement"
        )
    
    def notify_level_up(self, new_level: int) -> Notification:
        """Notify about level up."""
        return self.create_notification(
            title="⬆️ Level Up!",
            message=f"Congratulations! You've reached level {new_level}!",
            notification_type="milestone"
        )
    
    def notify_streak_milestone(self, streak_days: int) -> Notification:
        """Notify about streak milestone."""
        return self.create_notification(
            title="🔥 Streak Milestone!",
            message=f"Amazing! You've maintained a {streak_days}-day study streak!",
            notification_type="streak"
        )
    
    def notify_amcat_reminder(self) -> Notification:
        """Remind about AMCAT preparation."""
        return self.create_notification(
            title="💼 AMCAT Preparation",
            message="Don't forget to practice for your upcoming AMCAT exam!",
            notification_type="amcat"
        )
    
    def notify_missed_task(self, subject: str, topic: str) -> Notification:
        """Notify about a missed task."""
        return self.create_notification(
            title="⚠️ Task Missed",
            message=f"You missed studying {subject}: {topic}. Don't worry, it will be rescheduled.",
            notification_type="warning"
        )
    
    def notify_weekend_study(self) -> Notification:
        """Encourage weekend study."""
        return self.create_notification(
            title="🌟 Weekend Special",
            message="It's the weekend! Make the most of your free time with extra study sessions.",
            notification_type="motivation"
        )
