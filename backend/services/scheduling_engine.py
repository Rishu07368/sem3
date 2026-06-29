"""
Daily Timetable Scheduling Engine
A reusable, extensible engine for generating intelligent study schedules.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class StudyMode(str, Enum):
    """Study mode enumeration."""
    NORMAL = "normal"
    AMCAT = "amcat"
    EXAM = "exam"


@dataclass
class TimeSlot:
    """Represents a time slot in the daily schedule."""
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    activity: str
    is_fixed: bool = False
    flexible_end: Optional[str] = None

    def duration_minutes(self) -> int:
        start_h, start_m = map(int, self.start_time.split(':'))
        end_h, end_m = map(int, self.end_time.split(':'))
        return (end_h * 60 + end_m) - (start_h * 60 + start_m)


@dataclass
class Subject:
    """Represents a study subject with priority and syllabus breakdown."""
    name: str
    priority: int  # 1-7, lower is higher priority
    difficulty: float  # 1-10
    placement_importance: float  # 1-10
    target_hours_per_week: Tuple[float, float]  # min, max
    topics: List[str] = field(default_factory=list)
    is_amcat_subject: bool = False
    current_progress: float = 0.0  # 0-100
    confidence_level: float = 0.5  # 0-1
    completed_topics: List[str] = field(default_factory=list)


@dataclass
class StudyBlock:
    """Represents a scheduled study block."""
    subject: str
    topic: str
    start_time: str
    end_time: str
    duration_minutes: int
    is_amcat: bool = False
    is_revision: bool = False
    priority_override: Optional[int] = None


@dataclass
class DailySchedule:
    """Represents a complete daily schedule."""
    date: datetime
    time_slots: List[TimeSlot]
    study_blocks: List[StudyBlock]
    mode: StudyMode = StudyMode.NORMAL
    total_study_minutes: int = 0
    completion_percentage: float = 0.0


@dataclass
class SchedulingConstraints:
    """Configurable constraints for the scheduling engine."""
    # Date range
    start_date: datetime
    end_date: datetime
    
    # Fixed daily activities
    sleep_start: str = "23:30"
    sleep_end: str = "07:00"
    breakfast_start: str = "08:00"
    breakfast_end: str = "08:30"
    travel_to_college_start: str = "08:30"
    travel_to_college_end: str = "09:20"
    college_start: str = "09:30"
    college_end: str = "16:30"
    travel_back_start: str = "16:30"
    travel_back_end: str = "17:00"
    gym_start: str = "17:30"
    gym_end: str = "19:00"
    gym_extension: str = "19:30"
    dinner_start: str = "20:15"
    dinner_end: str = "20:45"
    
    # Study block priorities
    morning_revision_start: str = "07:15"
    morning_revision_end: str = "08:00"
    evening_study_start: str = "19:30"
    night_study_start: str = "20:45"
    night_study_end: str = "23:30"
    
    # AMCAT mode settings
    amcat_start_date: Optional[date] = None
    amcat_end_date: Optional[date] = None
    amcat_target_hours_per_week: float = 15.0
    
    # Exam mode settings
    exam_start_date: Optional[date] = None
    exam_weeks_before: int = 3
    
    # Weekly distribution
    total_available_study_hours: float = 30.0


class SchedulingEngine:
    """
    Core scheduling engine that generates intelligent daily timetables.
    
    This engine is:
    - Reusable: Works with any set of subjects and constraints
    - Extensible: Easy to add new scheduling strategies
    - Maintainable: Clear separation of concerns
    """
    
    def __init__(self, constraints: SchedulingConstraints):
        self.constraints = constraints
        self.subjects: Dict[str, Subject] = {}
        self.missed_tasks: List[Tuple[date, str, str]] = []
        
    def add_subject(self, subject: Subject) -> None:
        """Add a subject to the scheduling pool."""
        self.subjects[subject.name] = subject
    
    def remove_subject(self, name: str) -> None:
        """Remove a subject from the scheduling pool."""
        if name in self.subjects:
            del self.subjects[name]
    
    def get_mode_for_date(self, target_date: datetime) -> StudyMode:
        """Determine the study mode for a given date."""
        date_only = target_date.date() if isinstance(target_date, datetime) else target_date
        
        if self.constraints.exam_start_date:
            weeks_before = (self.constraints.exam_start_date - date_only).days / 7
            if weeks_before <= self.constraints.exam_weeks_before and weeks_before >= 0:
                return StudyMode.EXAM
        
        if self.constraints.amcat_start_date and self.constraints.amcat_end_date:
            if self.constraints.amcat_start_date <= date_only <= self.constraints.amcat_end_date:
                return StudyMode.AMCAT
        
        return StudyMode.NORMAL
    
    def get_study_hours_distribution(self, mode: StudyMode) -> Dict[str, float]:
        """Calculate weekly study hours distribution based on mode and priorities."""
        total_hours = self.constraints.total_available_study_hours
        
        if mode == StudyMode.AMCAT:
            return self._get_amcat_distribution(total_hours)
        elif mode == StudyMode.EXAM:
            return self._get_exam_distribution(total_hours)
        else:
            return self._get_normal_distribution(total_hours)
    
    def _get_normal_distribution(self, total_hours: float) -> Dict[str, float]:
        """Normal semester study distribution."""
        distribution = {}
        total_priority_score = sum(
            (8 - s.priority) * s.placement_importance * s.difficulty
            for s in self.subjects.values()
        )
        
        for name, subject in self.subjects.items():
            if subject.is_amcat_subject:
                continue
                
            priority_score = (8 - subject.priority) * subject.placement_importance * subject.difficulty
            share = priority_score / total_priority_score if total_priority_score > 0 else 0
            
            min_hours, max_hours = subject.target_hours_per_week
            target_hours = min_hours + (max_hours - min_hours) * subject.confidence_level
            
            distribution[name] = min(target_hours, max_hours)
        
        return self._normalize_distribution(distribution, total_hours)
    
    def _get_amcat_distribution(self, total_hours: float) -> Dict[str, float]:
        """AMCAT mode distribution - emphasizes aptitude and coding."""
        amcat_hours = self.constraints.amcat_target_hours_per_week
        remaining_hours = total_hours - amcat_hours
        
        distribution = {"AMCAT Practice": amcat_hours}
        
        # Distribute remaining hours to core subjects
        core_subjects = {k: v for k, v in self.subjects.items() if not v.is_amcat_subject}
        if core_subjects:
            core_distribution = self._get_normal_distribution(remaining_hours)
            distribution.update(core_distribution)
        
        return self._normalize_distribution(distribution, total_hours)
    
    def _get_exam_distribution(self, total_hours: float) -> Dict[str, float]:
        """Exam mode distribution - prioritizes weak subjects."""
        distribution = {}
        
        weak_subjects = [s for s in self.subjects.values() if s.current_progress < 50]
        strong_subjects = [s for s in self.subjects.values() if s.current_progress >= 50]
        
        weak_total = sum(s.difficulty for s in weak_subjects) if weak_subjects else 0
        strong_total = sum(s.difficulty for s in strong_subjects) if strong_subjects else 0
        total = weak_total + strong_total
        
        for subject in weak_subjects:
            share = (subject.difficulty / total) * total_hours if total > 0 else 0
            distribution[subject.name] = share * 1.5  # Boost weak subjects
        
        for subject in strong_subjects:
            share = (subject.difficulty / total) * total_hours if total > 0 else 0
            distribution[subject.name] = share * 0.5  # Reduce strong subjects
        
        return self._normalize_distribution(distribution, total_hours)
    
    def _normalize_distribution(self, distribution: Dict[str, float], total_hours: float) -> Dict[str, float]:
        """Normalize distribution to match total hours."""
        current_total = sum(distribution.values())
        if current_total == 0:
            return distribution
        
        scale = total_hours / current_total
        normalized = {k: v * scale for k, v in distribution.items()}
        
        # Ensure minimum 0.5 hours for any subject
        for name in normalized:
            if normalized[name] < 0.5:
                normalized[name] = 0.5
        
        return normalized
    
    def _select_primary_subject(self, target_date: datetime, distribution: Dict[str, float]) -> Optional[str]:
        """Select the primary subject for a study block based on rotation and priority."""
        day_of_week = target_date.weekday()
        
        # Rotate subjects based on day
        sorted_subjects = sorted(
            [(name, subj) for name, subj in self.subjects.items() if name in distribution],
            key=lambda x: (x[1].priority, x[0])
        )
        
        # Select based on day rotation
        index = day_of_week % len(sorted_subjects)
        return sorted_subjects[index][0] if sorted_subjects else None
    
    def _select_topic_for_subject(self, subject_name: str, target_date: datetime) -> str:
        """Select the next topic to study for a subject."""
        if subject_name not in self.subjects:
            return "General Revision"
        
        subject = self.subjects[subject_name]
        
        # Find uncompleted topics
        uncompleted = [t for t in subject.topics if t not in subject.completed_topics]
        
        if uncompleted:
            # Rotate through topics
            day_index = target_date.toordinal() % len(uncompleted)
            return uncompleted[day_index]
        
        # All topics completed, return a revision topic
        return f"Revision: {subject.topics[0]}"
    
    def _calculate_available_study_time(self, target_date: datetime) -> Dict[str, int]:
        """Calculate available study time slots for a day."""
        # Morning: 07:15 - 08:00 (45 minutes)
        # Evening: After gym (flexible) - 20:45
        # Night: 20:45 - 23:30 (165 minutes)
        
        available = {
            "morning": 45,  # 07:15 to 08:00
            "evening": 75,  # 19:30 to 20:45
            "night": 165,   # 20:45 to 23:30
        }
        
        return available
    
    def generate_fixed_time_slots(self, target_date: datetime) -> List[TimeSlot]:
        """Generate fixed time slots for a typical day."""
        slots = [
            TimeSlot("07:00", "08:00", "Morning Routine", is_fixed=True),
            TimeSlot("08:00", "08:30", "Breakfast", is_fixed=True),
            TimeSlot("08:30", "09:20", "Travel to College", is_fixed=True),
            TimeSlot("09:30", "16:30", "College Hours", is_fixed=True),
            TimeSlot("16:30", "17:00", "Travel Back", is_fixed=True),
            TimeSlot("17:30", "19:00", "Gym", is_fixed=True, flexible_end="19:30"),
            TimeSlot("20:15", "20:45", "Dinner", is_fixed=True),
        ]
        return slots
    
    def generate_daily_schedule(self, target_date: datetime) -> DailySchedule:
        """Generate a complete daily schedule for a given date."""
        mode = self.get_mode_for_date(target_date)
        distribution = self.get_study_hours_distribution(mode)
        available_time = self._calculate_available_study_time(target_date)
        
        # Calculate study minutes per block based on daily allocation
        day_of_week = target_date.weekday()
        is_weekend = day_of_week >= 5
        
        if is_weekend:
            # More study time on weekends
            morning_minutes = 90
            afternoon_minutes = 180
            evening_minutes = 120
        else:
            # Weekdays
            morning_minutes = 45
            afternoon_minutes = 75
            evening_minutes = 75
        
        study_blocks = []
        total_study_minutes = 0
        
        # Morning block
        primary = self._select_primary_subject(target_date, distribution)
        if primary:
            block = StudyBlock(
                subject=primary,
                topic=self._select_topic_for_subject(primary, target_date),
                start_time="07:15",
                end_time=self._add_minutes("07:15", morning_minutes),
                duration_minutes=morning_minutes,
                is_revision=mode == StudyMode.NORMAL
            )
            study_blocks.append(block)
            total_study_minutes += morning_minutes
        
        # Afternoon/Evening block (after gym)
        secondary = self._select_primary_subject(target_date, distribution)
        if secondary and secondary != primary:
            block = StudyBlock(
                subject=secondary,
                topic=self._select_topic_for_subject(secondary, target_date),
                start_time="19:30",
                end_time=self._add_minutes("19:30", afternoon_minutes),
                duration_minutes=afternoon_minutes,
                is_revision=False
            )
            study_blocks.append(block)
            total_study_minutes += afternoon_minutes
        
        # Night block
        tertiary = self._select_primary_subject(target_date, distribution)
        if tertiary:
            block = StudyBlock(
                subject=tertiary,
                topic=self._select_topic_for_subject(tertiary, target_date),
                start_time="20:45",
                end_time="23:30",
                duration_minutes=evening_minutes,
                is_revision=mode == StudyMode.NORMAL
            )
            study_blocks.append(block)
            total_study_minutes += evening_minutes
        
        # AMCAT mode - add practice block
        if mode == StudyMode.AMCAT:
            amcat_block = StudyBlock(
                subject="AMCAT Practice",
                topic="Sectional Test",
                start_time="21:30",
                end_time="23:30",
                duration_minutes=120,
                is_amcat=True
            )
            study_blocks.append(amcat_block)
            total_study_minutes += 120
        
        fixed_slots = self.generate_fixed_time_slots(target_date)
        
        return DailySchedule(
            date=target_date,
            time_slots=fixed_slots,
            study_blocks=study_blocks,
            mode=mode,
            total_study_minutes=total_study_minutes
        )
    
    def generate_timetable(self) -> List[DailySchedule]:
        """Generate complete timetable for the entire date range."""
        timetables = []
        current_date = self.constraints.start_date
        
        while current_date <= self.constraints.end_date:
            schedule = self.generate_daily_schedule(current_date)
            timetables.append(schedule)
            current_date += timedelta(days=1)
        
        return timetables
    
    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string and return new time string."""
        h, m = map(int, time_str.split(':'))
        total_mins = h * 60 + m + minutes
        new_h = (total_mins // 60) % 24
        new_m = total_mins % 60
        return f"{new_h:02d}:{new_m:02d}"
    
    def add_missed_task(self, target_date: date, subject: str, topic: str) -> None:
        """Record a missed task for future rescheduling."""
        self.missed_tasks.append((target_date, subject, topic))
    
    def get_semester_progress(self) -> Dict:
        """Get overall semester progress metrics."""
        total_days = (self.constraints.end_date.date() - self.constraints.start_date.date()).days + 1
        elapsed_days = (datetime.now().date() - self.constraints.start_date.date()).days + 1
        
        return {
            "total_days": total_days,
            "elapsed_days": max(0, elapsed_days),
            "remaining_days": max(0, total_days - elapsed_days),
            "progress_percentage": (max(0, elapsed_days) / total_days) * 100 if total_days > 0 else 0,
            "amcat_days_remaining": self._days_until_amcat(),
            "exam_days_remaining": self._days_until_exam(),
        }
    
    def _days_until_amcat(self) -> int:
        """Calculate days until AMCAT period starts."""
        if self.constraints.amcat_start_date:
            delta = self.constraints.amcat_start_date - datetime.now().date()
            return max(0, delta.days)
        return -1
    
    def _days_until_exam(self) -> int:
        """Calculate days until exam period starts."""
        if self.constraints.exam_start_date:
            delta = self.constraints.exam_start_date - datetime.now().date()
            return max(0, delta.days)
        return -1
