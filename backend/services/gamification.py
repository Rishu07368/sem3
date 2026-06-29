"""
Gamification Service
Implements XP, levels, achievements, and rewards system.
"""
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from models.database import User, Achievement, UserAchievement, StudyBlock, DailyMetrics


# XP rewards configuration
XP_REWARDS = {
    "study_block_complete": 50,
    "study_hour": 100,
    "daily_goal_complete": 75,
    "streak_day": 25,
    "subject_complete": 200,
    "topic_complete": 25,
    "pomodoro_complete": 15,
    "pomodoro_interrupt": -10,
    "task_missed": -20,
}


# Level thresholds
LEVEL_THRESHOLDS = [
    0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500,
    5500, 6600, 7800, 9100, 10500, 12000, 13600, 15300, 17100, 19000,
    21000, 23100, 25300, 27600, 30000, 32500, 35100, 37800, 40600, 43500,
]


@dataclass
class AchievementDefinition:
    """Defines an achievement."""
    code: str
    name: str
    description: str
    xp_reward: int
    icon: str
    category: str
    requirement_type: str
    requirement_value: int


# Default achievements
DEFAULT_ACHIEVEMENTS = [
    AchievementDefinition(
        code="FIRST_STEP",
        name="First Step",
        description="Complete your first study block",
        xp_reward=50,
        icon="star",
        category="milestone",
        requirement_type="study_blocks",
        requirement_value=1,
    ),
    AchievementDefinition(
        code="EARLY_BIRD",
        name="Early Bird",
        description="Study before 8 AM",
        xp_reward=30,
        icon="sunrise",
        category="habit",
        requirement_type="early_study",
        requirement_value=1,
    ),
    AchievementDefinition(
        code="NIGHT_OWL",
        name="Night Owl",
        description="Study after 11 PM",
        xp_reward=30,
        icon="moon",
        category="habit",
        requirement_type="late_study",
        requirement_value=1,
    ),
    AchievementDefinition(
        code="STREAK_3",
        name="Getting Started",
        description="Maintain a 3-day study streak",
        xp_reward=100,
        icon="flame",
        category="streak",
        requirement_type="streak",
        requirement_value=3,
    ),
    AchievementDefinition(
        code="STREAK_7",
        name="Week Warrior",
        description="Maintain a 7-day study streak",
        xp_reward=250,
        icon="fire",
        category="streak",
        requirement_type="streak",
        requirement_value=7,
    ),
    AchievementDefinition(
        code="STREAK_30",
        name="Monthly Master",
        description="Maintain a 30-day study streak",
        xp_reward=1000,
        icon="trophy",
        category="streak",
        requirement_type="streak",
        requirement_value=30,
    ),
    AchievementDefinition(
        code="HOURS_10",
        name="Dedicated Learner",
        description="Study for 10 total hours",
        xp_reward=200,
        icon="clock",
        category="hours",
        requirement_type="total_hours",
        requirement_value=10,
    ),
    AchievementDefinition(
        code="HOURS_50",
        name="Study Enthusiast",
        description="Study for 50 total hours",
        xp_reward=500,
        icon="book-open",
        category="hours",
        requirement_type="total_hours",
        requirement_value=50,
    ),
    AchievementDefinition(
        code="HOURS_100",
        name="Scholar",
        description="Study for 100 total hours",
        xp_reward=1500,
        icon="graduation-cap",
        category="hours",
        requirement_type="total_hours",
        requirement_value=100,
    ),
    AchievementDefinition(
        code="POMODORO_10",
        name="Focused Mind",
        description="Complete 10 pomodoro sessions",
        xp_reward=100,
        icon="timer",
        category="pomodoro",
        requirement_type="pomodoro",
        requirement_value=10,
    ),
    AchievementDefinition(
        code="POMODORO_50",
        name="Concentration Master",
        description="Complete 50 pomodoro sessions",
        xp_reward=400,
        icon="zap",
        category="pomodoro",
        requirement_type="pomodoro",
        requirement_value=50,
    ),
    AchievementDefinition(
        code="TOPIC_10",
        name="Knowledge Seeker",
        description="Complete 10 topics",
        xp_reward=150,
        icon="check-circle",
        category="topics",
        requirement_type="topics",
        requirement_value=10,
    ),
    AchievementDefinition(
        code="TOPIC_50",
        name="Topic Champion",
        description="Complete 50 topics",
        xp_reward=750,
        icon="award",
        category="topics",
        requirement_type="topics",
        requirement_value=50,
    ),
    AchievementDefinition(
        code="ADSA_MASTER",
        name="ADSA Master",
        description="Complete all ADSA topics",
        xp_reward=500,
        icon="code",
        category="subject",
        requirement_value=20,  # All ADSA topics
    ),
    AchievementDefinition(
        code="DBMS_MASTER",
        name="Database Expert",
        description="Complete all DBMS topics",
        xp_reward=400,
        icon="database",
        category="subject",
        requirement_type="subject_topics",
        requirement_value=8,
    ),
    AchievementDefinition(
        code="COA_MASTER",
        name="Architecture Expert",
        description="Complete all COA topics",
        xp_reward=400,
        icon="cpu",
        category="subject",
        requirement_type="subject_topics",
        requirement_value=10,
    ),
    AchievementDefinition(
        code="LEVEL_5",
        name="Rising Star",
        description="Reach level 5",
        xp_reward=200,
        icon="star",
        category="level",
        requirement_type="level",
        requirement_value=5,
    ),
    AchievementDefinition(
        code="LEVEL_10",
        name="Study Expert",
        description="Reach level 10",
        xp_reward=500,
        icon="award",
        category="level",
        requirement_type="level",
        requirement_value=10,
    ),
    AchievementDefinition(
        code="PERFECT_DAY",
        name="Perfect Day",
        description="Complete all planned study blocks in a day",
        xp_reward=150,
        icon="check-square",
        category="milestone",
        requirement_type="perfect_day",
        requirement_value=1,
    ),
    AchievementDefinition(
        code="AMCAT_PREP",
        name="AMCAT Ready",
        description="Complete AMCAT preparation",
        xp_reward=300,
        icon="clipboard-check",
        category="milestone",
        requirement_type="amcat",
        requirement_value=1,
    ),
]


class GamificationService:
    """
    Handles gamification logic including XP, levels, and achievements.
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def _get_user(self) -> User:
        """Get the user object."""
        return self.db.query(User).filter(User.id == self.user_id).first()
    
    def add_xp(self, amount: int, reason: str = "") -> Dict:
        """Add XP to the user and check for level up."""
        user = self._get_user()
        if not user:
            raise ValueError("User not found")
        
        old_level = user.level
        user.xp = max(0, user.xp + amount)
        
        # Calculate new level
        new_level = self._calculate_level(user.xp)
        user.level = new_level
        
        leveled_up = new_level > old_level
        
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "xp_added": amount,
            "total_xp": user.xp,
            "old_level": old_level,
            "new_level": new_level,
            "leveled_up": leveled_up,
            "xp_to_next_level": self.xp_for_level(new_level + 1) - user.xp if new_level < len(LEVEL_THRESHOLDS) - 1 else 0,
        }
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP."""
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if xp < threshold:
                return i
        return len(LEVEL_THRESHOLDS) - 1
    
    def xp_for_level(self, level: int) -> int:
        """Get XP required for a specific level."""
        if level < len(LEVEL_THRESHOLDS):
            return LEVEL_THRESHOLDS[level]
        return LEVEL_THRESHOLDS[-1]
    
    def get_user_stats(self) -> Dict:
        """Get gamification stats for the user."""
        user = self._get_user()
        if not user:
            raise ValueError("User not found")
        
        level = self._calculate_level(user.xp)
        xp_for_next = self.xp_for_level(level + 1) if level < len(LEVEL_THRESHOLDS) - 1 else user.xp
        progress_to_next = ((user.xp - self.xp_for_level(level)) / (xp_for_next - self.xp_for_level(level)) * 100) if xp_for_next > self.xp_for_level(level) else 100
        
        return {
            "xp": user.xp,
            "level": level,
            "level_name": self._get_level_name(level),
            "xp_for_next_level": xp_for_next - user.xp,
            "xp_progress_percentage": progress_to_next,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
        }
    
    def _get_level_name(self, level: int) -> str:
        """Get a fun name for the level."""
        names = [
            "Novice", "Beginner", "Apprentice", "Student", "Scholar",
            "Expert", "Master", "Guru", "Sage", "Legend",
            "Mythic", "Divine", "Celestial", "Eternal", "Infinite",
        ]
        return names[min(level, len(names) - 1)]
    
    def award_xp_for_block_complete(self, block: StudyBlock) -> Dict:
        """Award XP for completing a study block."""
        base_xp = XP_REWARDS["study_block_complete"]
        
        # Bonus for longer blocks
        duration_bonus = (block.duration_minutes / 30) * 10
        
        # Bonus for revision
        revision_bonus = 20 if block.is_revision else 0
        
        total_xp = int(base_xp + duration_bonus + revision_bonus)
        
        return self.add_xp(total_xp, f"Completed {block.subject}: {block.topic}")
    
    def award_xp_for_pomodoro(self, duration_minutes: int, completed: bool = True) -> Dict:
        """Award XP for pomodoro session."""
        if completed:
            xp = XP_REWARDS["pomodoro_complete"]
        else:
            xp = XP_REWARDS["pomodoro_interrupt"]
        
        return self.add_xp(xp, "Pomodoro session")
    
    def check_and_award_achievements(self) -> List[Dict]:
        """Check for new achievements and award them."""
        user = self._get_user()
        if not user:
            return []
        
        new_achievements = []
        earned_codes = {ua.achievement.code for ua in user.achievements}
        
        # Get user stats
        stats = self._get_user_stats()
        
        # Check each achievement
        for ach in DEFAULT_ACHIEVEMENTS:
            if ach.code in earned_codes:
                continue
            
            earned = False
            
            if ach.requirement_type == "streak":
                earned = user.current_streak >= ach.requirement_value
            elif ach.requirement_type == "level":
                earned = stats["level"] >= ach.requirement_value
            elif ach.requirement_type == "total_hours":
                # Calculate from metrics
                total_hours = self._get_total_study_hours()
                earned = total_hours >= ach.requirement_value
            elif ach.requirement_type == "study_blocks":
                completed_blocks = self._count_completed_blocks()
                earned = completed_blocks >= ach.requirement_value
            elif ach.requirement_type == "pomodoro":
                pomodoros = self._count_pomodoros()
                earned = pomodoros >= ach.requirement_value
            elif ach.requirement_type == "topics":
                topics = self._count_completed_topics()
                earned = topics >= ach.requirement_value
            
            if earned:
                # Create achievement in database
                db_ach = self.db.query(Achievement).filter(
                    Achievement.code == ach.code
                ).first()
                
                if not db_ach:
                    db_ach = Achievement(
                        code=ach.code,
                        name=ach.name,
                        description=ach.description,
                        xp_reward=ach.xp_reward,
                        icon=ach.icon,
                        category=ach.category,
                        requirement_type=ach.requirement_type,
                        requirement_value=ach.requirement_value,
                    )
                    self.db.add(db_ach)
                
                # Award to user
                user_ach = UserAchievement(
                    user_id=user.id,
                    achievement_id=db_ach.id,
                )
                self.db.add(user_ach)
                
                # Award XP
                self.add_xp(ach.xp_reward, f"Achievement: {ach.name}")
                
                new_achievements.append({
                    "code": ach.code,
                    "name": ach.name,
                    "description": ach.description,
                    "xp_reward": ach.xp_reward,
                    "icon": ach.icon,
                })
        
        self.db.commit()
        return new_achievements
    
    def _get_total_study_hours(self) -> float:
        """Get total study hours from metrics."""
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id
        ).all()
        total_minutes = sum(m.total_study_minutes for m in metrics)
        return total_minutes / 60
    
    def _count_completed_blocks(self) -> int:
        """Count completed study blocks."""
        return self.db.query(StudyBlock).filter(
            StudyBlock.user_id == self.user_id,
            StudyBlock.completed == True
        ).count()
    
    def _count_pomodoros(self) -> int:
        """Count completed pomodoro sessions."""
        from models.database import PomodoroSession
        return self.db.query(PomodoroSession).filter(
            PomodoroSession.user_id == self.user_id,
            PomodoroSession.status == "completed"
        ).count()
    
    def _count_completed_topics(self) -> int:
        """Count completed topics from subject progress."""
        from models.database import SubjectProgress
        import json
        progress = self.db.query(SubjectProgress).filter(
            SubjectProgress.user_id == self.user_id
        ).all()
        return sum(len(json.loads(p.completed_topics or "[]")) for p in progress)
    
    def get_user_achievements(self) -> List[Dict]:
        """Get all achievements for the user."""
        user = self._get_user()
        if not user:
            return []
        
        achievements = []
        for ua in user.achievements:
            achievements.append({
                "id": ua.achievement.id,
                "code": ua.achievement.code,
                "name": ua.achievement.name,
                "description": ua.achievement.description,
                "icon": ua.achievement.icon,
                "category": ua.achievement.category,
                "xp_reward": ua.achievement.xp_reward,
                "earned_at": ua.earned_at.isoformat(),
            })
        
        return achievements
    
    def get_available_achievements(self) -> List[Dict]:
        """Get achievements the user hasn't earned yet."""
        user = self._get_user()
        if not user:
            return []
        
        earned_codes = {ua.achievement.code for ua in user.achievements}
        
        available = []
        for ach in DEFAULT_ACHIEVEMENTS:
            if ach.code not in earned_codes:
                available.append({
                    "code": ach.code,
                    "name": ach.name,
                    "description": ach.description,
                    "icon": ach.icon,
                    "category": ach.category,
                    "xp_reward": ach.xp_reward,
                    "requirement_type": ach.requirement_type,
                    "requirement_value": ach.requirement_value,
                })
        
        return available
    
    def update_streak(self) -> Dict:
        """Update the user's study streak."""
        user = self._get_user()
        if not user:
            raise ValueError("User not found")
        
        today = datetime.now().date()
        
        # Check if studied today
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date == today
        ).first()
        
        studied_today = metrics and metrics.tasks_completed > 0
        
        # Check if studied yesterday
        yesterday = today - timedelta(days=1)
        yesterday_metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date == yesterday
        ).first()
        
        studied_yesterday = yesterday_metrics and yesterday_metrics.tasks_completed > 0
        
        if studied_today:
            if studied_yesterday:
                # Continue streak
                user.current_streak += 1
            else:
                # Start new streak
                user.current_streak = 1
            
            # Update longest streak
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
        
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
        }
    
    def get_daily_missions(self) -> List[Dict]:
        """Get daily missions for the user."""
        today = datetime.now().date()
        
        # Get today's metrics
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date == today
        ).first()
        
        blocks_completed = metrics.tasks_completed if metrics else 0
        study_minutes = metrics.total_study_minutes if metrics else 0
        
        return [
            {
                "id": "daily_blocks",
                "title": "Complete Study Blocks",
                "description": "Finish your scheduled study blocks",
                "target": 3,
                "progress": blocks_completed,
                "xp_reward": 100,
                "completed": blocks_completed >= 3,
            },
            {
                "id": "daily_hours",
                "title": "Study Hours",
                "description": "Study for at least 3 hours",
                "target": 180,
                "progress": study_minutes,
                "xp_reward": 150,
                "completed": study_minutes >= 180,
            },
            {
                "id": "daily_streak",
                "title": "Maintain Streak",
                "description": "Study today to keep your streak alive",
                "target": 1,
                "progress": 1 if blocks_completed > 0 else 0,
                "xp_reward": 50,
                "completed": blocks_completed > 0,
            },
        ]
    
    def get_weekly_missions(self) -> List[Dict]:
        """Get weekly missions for the user."""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Get this week's metrics
        metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.user_id == self.user_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= today
        ).all()
        
        total_hours = sum(m.total_study_minutes for m in metrics) / 60
        total_blocks = sum(m.tasks_completed for m in metrics)
        
        return [
            {
                "id": "weekly_hours",
                "title": "Weekly Study Goal",
                "description": "Study for 20 hours this week",
                "target": 20,
                "progress": total_hours,
                "xp_reward": 500,
                "completed": total_hours >= 20,
            },
            {
                "id": "weekly_blocks",
                "title": "Weekly Blocks",
                "description": "Complete 20 study blocks this week",
                "target": 20,
                "progress": total_blocks,
                "xp_reward": 300,
                "completed": total_blocks >= 20,
            },
        ]
