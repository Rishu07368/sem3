"""
Daily Timetable Scheduling Engine
A reusable, extensible engine for generating intelligent study schedules.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class StudyMode(Enum):
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
    flexible_end: Optional[str] = None  # For gym extension

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
    evening_study_start: str = "17:30"  # After gym
    night_study_start: str = "20:45"    # After dinner
    night_study_end: str = "23:30"      # Before sleep
    
    # AMCAT mode settings
    amcat_start_date: Optional[datetime] = None
    amcat_end_date: Optional[datetime] = None
    amcat_target_hours_per_week: float = 15.0
    
    # Exam mode settings
    exam_start_date: Optional[datetime] = None
    exam_weeks_before: int = 3
    
    # Weekly distribution
    total_available_study_hours: float = 30.0  # Total study hours per week


@dataclass 
class SyllabusProgress:
    """Tracks progress through each subject's syllabus."""
    subject: str
    total_topics: int
    completed_topics: List[str]
    confidence_scores: Dict[str, float]  # topic -> confidence (0-1)
    
    def completion_percentage(self) -> float:
        if self.total_topics == 0:
            return 0.0
        return (len(self.completed_topics) / self.total_topics) * 100
    
    def weak_topics(self) -> List[str]:
        return [t for t, c in self.confidence_scores.items() if c < 0.6]


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
        self.syllabus_progress: Dict[str, SyllabusProgress] = {}
        self.missed_tasks: List[Tuple[datetime, str, str]] = []  # (date, subject, topic)
        
    def add_subject(self, subject: Subject) -> None:
        """Add a subject to the scheduling pool."""
        self.subjects[subject.name] = subject
        self.syllabus_progress[subject.name] = SyllabusProgress(
            subject=subject.name,
            total_topics=len(subject.topics),
            completed_topics=subject.completed_topics.copy(),
            confidence_scores={t: subject.confidence_level for t in subject.topics}
        )
    
    def remove_subject(self, name: str) -> None:
        """Remove a subject from the scheduling pool."""
        if name in self.subjects:
            del self.subjects[name]
            del self.syllabus_progress[name]
    
    def get_mode_for_date(self, date: datetime) -> StudyMode:
        """Determine the study mode for a given date."""
        date_only = date.date() if isinstance(date, datetime) else date
        
        if self.constraints.exam_start_date:
            weeks_before = (self.constraints.exam_start_date - date_only).days / 7
            if weeks_before <= self.constraints.exam_weeks_before and weeks_before >= 0:
                return StudyMode.EXAM
        
        if self.constraints.amcat_start_date and self.constraints.amcat_end_date:
            if self.constraints.amcat_start_date <= date_only <= self.constraints.amcat_end_date:
                return StudyMode.AMCAT
        
        return StudyMode.NORMAL
    
    def get_study_hours_distribution(self, mode: StudyMode) -> Dict[str, float]:
        """
        Calculate weekly study hours distribution based on mode and priorities.
        Harder subjects with higher placement importance get more hours.
        """
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
                continue  # Skip AMCAT subjects in normal mode
                
            priority_score = (8 - subject.priority) * subject.placement_importance * subject.difficulty
            share = priority_score / total_priority_score if total_priority_score > 0 else 0
            
            # Use subject's target range, adjusted by priority
            min_hours, max_hours = subject.target_hours_per_week
            target_hours = min_hours + (max_hours - min_hours) * subject.confidence_level
            
            distribution[name] = min(target_hours, max_hours)
        
        return self._normalize_distribution(distribution, total_hours)
    
    def _get_amcat_distribution(self, total_hours: float) -> Dict[str, float]:
        """AMCAT mode distribution - emphasizes aptitude and coding."""
        # AMCAT subjects get significant time
        amcat_hours = self.constraints.amcat_target_hours_per_week
        remaining_hours = total_hours - amcat_hours
        
        distribution = {
            "Quantitative Aptitude": amcat_hours * 0.30,
            "Logical Reasoning": amcat_hours * 0.25,
            "English": amcat_hours * 0.15,
            "Coding Problems": amcat_hours * 0.15,
            "Debugging": amcat_hours * 0.10,
            "Core CS Revision": amcat_hours * 0.05,
        }
        
        # Reduce normal subjects but maintain minimum progress
        normal_subjects = {k: v for k, v in self.subjects.items() if not self.subjects[k].is_amcat_subject}
        if normal_subjects:
            per_subject = remaining_hours / len(normal_subjects)
            for name in normal_subjects:
                min_hours, _ = normal_subjects[name].target_hours_per_week
                distribution[name] = max(per_subject, min_hours * 0.5)
        
        return self._normalize_distribution(distribution, total_hours)
    
    def _get_exam_distribution(self, total_hours: float) -> Dict[str, float]:
        """Exam mode distribution - emphasizes revision and mock papers."""
        distribution = {
            "Revision": total_hours * 0.35,
            "Mock Papers": total_hours * 0.25,
            "Weak Topics": total_hours * 0.20,
            "Previous Year Questions": total_hours * 0.15,
            "New Learning": total_hours * 0.05,
        }
        
        # Distribute to actual subjects based on weak topics
        weak_subject_hours = total_hours * 0.40
        subjects_with_weak = [(n, len(self.syllabus_progress[n].weak_topics())) 
                              for n in self.subjects if self.syllabus_progress[n].weak_topics()]
        
        if subjects_with_weak:
            total_weak = sum(w for _, w in subjects_with_weak)
            for name, weak_count in subjects_with_weak:
                distribution[name] = (weak_count / total_weak) * weak_subject_hours if total_weak > 0 else 0
        
        return self._normalize_distribution(distribution, total_hours)
    
    def _normalize_distribution(self, distribution: Dict[str, float], 
                                total_hours: float) -> Dict[str, float]:
        """Normalize distribution to match total hours."""
        current_total = sum(distribution.values())
        if current_total == 0:
            return distribution
        
        scale = total_hours / current_total
        for key in distribution:
            distribution[key] *= scale
        
        return distribution
    
    def generate_daily_schedule(self, date: datetime) -> DailySchedule:
        """Generate a complete daily schedule for a given date."""
        mode = self.get_mode_for_date(date)
        study_hours = self.get_study_hours_distribution(mode)
        
        # Build fixed time slots
        time_slots = self._build_fixed_time_slots(date)
        
        # Generate study blocks
        study_blocks = self._generate_study_blocks(date, mode, study_hours)
        
        # Calculate totals
        total_study_minutes = sum(b.duration_minutes for b in study_blocks)
        
        schedule = DailySchedule(
            date=date,
            time_slots=time_slots,
            study_blocks=study_blocks,
            mode=mode,
            total_study_minutes=total_study_minutes
        )
        
        return schedule
    
    def _build_fixed_time_slots(self, date: datetime) -> List[TimeSlot]:
        """Build the fixed daily time slots."""
        return [
            TimeSlot(
                start_time=self.constraints.sleep_start,
                end_time="23:59",
                activity="Sleep",
                is_fixed=True
            ),
            TimeSlot(
                start_time="00:00",
                end_time=self.constraints.sleep_end,
                activity="Sleep",
                is_fixed=True
            ),
            TimeSlot(
                start_time=self.constraints.breakfast_start,
                end_time=self.constraints.breakfast_end,
                activity="Breakfast",
                is_fixed=True
            ),
            TimeSlot(
                start_time=self.constraints.travel_to_college_start,
                end_time=self.constraints.travel_to_college_end,
                activity="Travel to College",
                is_fixed=True
            ),
            TimeSlot(
                start_time=self.constraints.college_start,
                end_time=self.constraints.college_end,
                activity="College",
                is_fixed=True
            ),
            TimeSlot(
                start_time=self.constraints.travel_back_start,
                end_time=self.constraints.travel_back_end,
                activity="Travel Back",
                is_fixed=True
            ),
            TimeSlot(
                start_time=self.constraints.gym_start,
                end_time=self.constraints.gym_end,
                activity="Gym",
                is_fixed=True,
                flexible_end=self.constraints.gym_extension
            ),
            TimeSlot(
                start_time=self.constraints.dinner_start,
                end_time=self.constraints.dinner_end,
                activity="Dinner",
                is_fixed=True
            ),
        ]
    
    def _generate_study_blocks(self, date: datetime, mode: StudyMode,
                               study_hours: Dict[str, float]) -> List[StudyBlock]:
        """Generate study blocks for the day based on mode and priorities."""
        blocks = []
        
        if mode == StudyMode.AMCAT:
            blocks.extend(self._generate_amcat_blocks(date, study_hours))
        elif mode == StudyMode.EXAM:
            blocks.extend(self._generate_exam_blocks(date, study_hours))
        else:
            blocks.extend(self._generate_normal_blocks(date, study_hours))
        
        # Check for missed tasks to reschedule
        blocks.extend(self._reschedule_missed_tasks(date))
        
        return blocks
    
    def _generate_normal_blocks(self, date: datetime, 
                                study_hours: Dict[str, float]) -> List[StudyBlock]:
        """Generate study blocks for normal mode."""
        blocks = []
        
        # Morning revision block (45 minutes)
        morning_subject = self._select_subject_for_slot(study_hours, date, "morning")
        if morning_subject:
            blocks.append(StudyBlock(
                subject=morning_subject,
                topic=self._select_topic_for_subject(morning_subject, date),
                start_time=self.constraints.morning_revision_start,
                end_time=self.constraints.morning_revision_end,
                duration_minutes=45,
                is_revision=True
            ))
        
        # Evening study block (after gym)
        evening_subject = self._select_subject_for_slot(study_hours, date, "evening")
        if evening_subject:
            # Available: 17:30 to 20:15 (dinner), minus gym if still going
            blocks.append(StudyBlock(
                subject=evening_subject,
                topic=self._select_topic_for_subject(evening_subject, date),
                start_time="17:30",
                end_time="20:15",
                duration_minutes=165,
                is_revision=False
            ))
        
        # Night study block (after dinner)
        night_hours = self._calculate_night_study_available()
        if night_hours > 0:
            night_subject = self._select_subject_for_slot(study_hours, date, "night")
            if night_subject:
                # Split night block into multiple subjects if time allows
                split_blocks = self._split_night_block(night_subject, night_hours, date)
                blocks.extend(split_blocks)
        
        # Add AMCAT practice if AMCAT date is approaching
        if self.constraints.amcat_start_date:
            date_only = date.date() if isinstance(date, datetime) else date
            days_to_amcat = (self.constraints.amcat_start_date - date_only).days
            if 0 < days_to_amcat <= 14:  # Start AMCAT prep 2 weeks before
                blocks.append(self._create_amcat_block(date, min(days_to_amcat / 2, 2)))
        
        return blocks
    
    def _generate_amcat_blocks(self, date: datetime, 
                               study_hours: Dict[str, float]) -> List[StudyBlock]:
        """Generate study blocks for AMCAT mode."""
        blocks = []
        
        # Morning: Quantitative Aptitude
        blocks.append(StudyBlock(
            subject="Quantitative Aptitude",
            topic="Number Systems & Progressions",
            start_time=self.constraints.morning_revision_start,
            end_time=self.constraints.morning_revision_end,
            duration_minutes=45,
            is_amcat=True
        ))
        
        # Evening: AMCAT focus (3 hours)
        amcat_evening = [
            ("Logical Reasoning", "Coding Problems", 90),
            ("English", "Core CS Revision", 75)
        ]
        
        start_time = datetime.strptime("17:30", "%H:%M")
        for subject, topic, duration in amcat_evening:
            end_time = start_time + timedelta(minutes=duration)
            blocks.append(StudyBlock(
                subject=subject,
                topic=topic,
                start_time=start_time.strftime("%H:%M"),
                end_time=end_time.strftime("%H:%M"),
                duration_minutes=duration,
                is_amcat=True
            ))
            start_time = end_time + timedelta(minutes=15)  # 15 min break
        
        # Night: Mixed AMCAT practice
        night_available = self._calculate_night_study_available()
        if night_available > 60:
            blocks.append(StudyBlock(
                subject="AMCAT Practice",
                topic="Mock Test & Analysis",
                start_time="20:45",
                end_time="23:30",
                duration_minutes=165,
                is_amcat=True
            ))
        
        return blocks
    
    def _generate_exam_blocks(self, date: datetime, 
                              study_hours: Dict[str, float]) -> List[StudyBlock]:
        """Generate study blocks for exam mode."""
        blocks = []
        
        # Morning: Quick revision
        blocks.append(StudyBlock(
            subject="Revision",
            topic=self._get_weakest_topic(date),
            start_time=self.constraints.morning_revision_start,
            end_time=self.constraints.morning_revision_end,
            duration_minutes=45,
            is_revision=True
        ))
        
        # Evening: Mock papers and weak topics
        blocks.append(StudyBlock(
            subject="Mock Papers",
            topic="Previous Year Questions",
            start_time="17:30",
            end_time="20:15",
            duration_minutes=165,
            is_revision=True
        ))
        
        # Night: Deep revision
        night_available = self._calculate_night_study_available()
        if night_available > 90:
            blocks.append(StudyBlock(
                subject="Weak Topics",
                topic=self._get_weakest_topic(date),
                start_time="20:45",
                end_time="23:30",
                duration_minutes=165,
                is_revision=True
            ))
        
        return blocks
    
    def _select_subject_for_slot(self, study_hours: Dict[str, float],
                                 date: datetime, slot_type: str) -> Optional[str]:
        """Select the best subject for a given time slot based on priority."""
        # Filter out subjects with no hours allocated
        available = {k: v for k, v in study_hours.items() if v > 0}
        
        if not available:
            return None
        
        # Get day of week (0=Mon, 6=Sun)
        day_of_week = date.weekday()
        
        # Rotate subjects based on day to ensure variety
        sorted_subjects = sorted(available.items(), key=lambda x: x[1], reverse=True)
        
        # Add some rotation based on day
        rotation_offset = (day_of_week * 2 + (1 if slot_type == "morning" else 0)) % len(sorted_subjects)
        
        # Return highest priority subject with some rotation
        if sorted_subjects:
            # Primary selection from top priorities
            for subject, hours in sorted_subjects[:3]:
                if subject in self.subjects:
                    return subject
            return sorted_subjects[0][0]
        
        return None
    
    def _select_topic_for_subject(self, subject_name: str, date: datetime) -> str:
        """Select the best topic for a subject based on progress and spaced repetition."""
        if subject_name not in self.syllabus_progress:
            return "General Study"
        
        progress = self.syllabus_progress[subject_name]
        incomplete_topics = [t for t in progress.confidence_scores.keys() 
                            if t not in progress.completed_topics]
        
        if not incomplete_topics:
            return "Revision"  # All topics done, focus on revision
        
        # Prioritize topics with lower confidence (spaced repetition)
        weakest = min(incomplete_topics, 
                     key=lambda t: progress.confidence_scores.get(t, 0.5))
        
        return weakest
    
    def _calculate_night_study_available(self) -> int:
        """Calculate available minutes for night study block."""
        night_start = self.constraints.night_study_start
        sleep_start = self.constraints.sleep_start
        
        start_h, start_m = map(int, night_start.split(':'))
        end_h, end_m = map(int, sleep_start.split(':'))
        
        return (end_h * 60 + end_m) - (start_h * 60 + start_m)
    
    def _split_night_block(self, subject: str, available_minutes: int,
                          date: datetime) -> List[StudyBlock]:
        """Split night study time across multiple subjects if needed."""
        blocks = []
        
        # Main subject gets 60% of time
        main_duration = int(available_minutes * 0.6)
        blocks.append(StudyBlock(
            subject=subject,
            topic=self._select_topic_for_subject(subject, date),
            start_time=self.constraints.night_study_start,
            end_time=self._add_minutes(self.constraints.night_study_start, main_duration),
            duration_minutes=main_duration
        ))
        
        # Secondary subject gets remaining 40%
        remaining = available_minutes - main_duration
        if remaining >= 45:
            # Find a secondary subject
            secondary = self._select_secondary_subject(subject, date)
            if secondary:
                blocks.append(StudyBlock(
                    subject=secondary,
                    topic=self._select_topic_for_subject(secondary, date),
                    start_time=self._add_minutes(self.constraints.night_study_start, main_duration),
                    end_time=self._add_minutes(self.constraints.night_study_start, available_minutes),
                    duration_minutes=remaining,
                    is_revision=True
                ))
        
        return blocks
    
    def _select_secondary_subject(self, primary: str, date: datetime) -> Optional[str]:
        """Select a secondary subject for variety."""
        remaining = [s for s in self.subjects.keys() if s != primary]
        
        if not remaining:
            return None
        
        # Rotate based on day
        day_index = date.weekday()
        return remaining[day_index % len(remaining)]
    
    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string and return new time string."""
        h, m = map(int, time_str.split(':'))
        total_mins = h * 60 + m + minutes
        new_h = (total_mins // 60) % 24
        new_m = total_mins % 60
        return f"{new_h:02d}:{new_m:02d}"
    
    def _create_amcat_block(self, date: datetime, target_hours: float) -> StudyBlock:
        """Create an AMCAT practice block."""
        return StudyBlock(
            subject="AMCAT Practice",
            topic="Sectional Test",
            start_time="20:45",
            end_time=self._add_minutes("20:45", int(target_hours * 60)),
            duration_minutes=int(target_hours * 60),
            is_amcat=True
        )
    
    def _get_weakest_topic(self, date: datetime) -> str:
        """Get the weakest topic across all subjects."""
        weakest = None
        min_confidence = 1.0
        
        for subject, progress in self.syllabus_progress.items():
            for topic, confidence in progress.confidence_scores.items():
                if confidence < min_confidence:
                    min_confidence = confidence
                    weakest = topic
        
        return weakest or "General Revision"
    
    def _reschedule_missed_tasks(self, current_date: datetime) -> List[StudyBlock]:
        """Reschedule missed tasks to the best available future slot."""
        blocks = []
        
        # Find missed tasks that should be rescheduled
        tasks_to_reschedule = [
            (d, s, t) for d, s, t in self.missed_tasks 
            if d >= current_date - timedelta(days=7)  # Within last week
        ]
        
        # Limit to avoid overload
        tasks_to_reschedule = tasks_to_reschedule[:2]
        
        for missed_date, subject, topic in tasks_to_reschedule:
            # Find next available slot
            if self._has_available_slot(current_date):
                blocks.append(StudyBlock(
                    subject=subject,
                    topic=topic,
                    start_time="21:00",
                    end_time="22:00",
                    duration_minutes=60,
                    is_revision=True
                ))
        
        return blocks
    
    def _has_available_slot(self, date: datetime) -> bool:
        """Check if there's an available study slot."""
        available = self._calculate_night_study_available()
        return available >= 60
    
    def generate_timetable(self) -> List[DailySchedule]:
        """Generate complete timetable for the entire date range."""
        timetables = []
        current_date = self.constraints.start_date
        
        while current_date <= self.constraints.end_date:
            schedule = self.generate_daily_schedule(current_date)
            timetables.append(schedule)
            current_date += timedelta(days=1)
        
        return timetables
    
    def update_progress(self, subject_name: str, topic: str, 
                        completed: bool, confidence: float = 0.0) -> None:
        """Update progress for a subject/topic."""
        if subject_name in self.syllabus_progress:
            progress = self.syllabus_progress[subject_name]
            
            if completed and topic not in progress.completed_topics:
                progress.completed_topics.append(topic)
            
            if confidence > 0:
                progress.confidence_scores[topic] = confidence
            
            # Update subject's current progress
            if subject_name in self.subjects:
                self.subjects[subject_name].current_progress = progress.completion_percentage()
    
    def add_missed_task(self, date: datetime, subject: str, topic: str) -> None:
        """Record a missed task for future rescheduling."""
        self.missed_tasks.append((date, subject, topic))
    
    def get_subject_weekly_progress(self, subject_name: str, 
                                    hours_allocated: float) -> Dict:
        """Get progress metrics for a subject."""
        if subject_name not in self.syllabus_progress:
            return {}
        
        progress = self.syllabus_progress[subject_name]
        
        return {
            "subject": subject_name,
            "total_topics": progress.total_topics,
            "completed_topics": len(progress.completed_topics),
            "completion_percentage": progress.completion_percentage(),
            "weak_topics": progress.weak_topics(),
            "hours_allocated_this_week": hours_allocated,
            "predicted_completion": self._predict_completion(progress, hours_allocated)
        }
    
    def _predict_completion(self, progress: SyllabusProgress, 
                           weekly_hours: float) -> datetime:
        """Predict when a subject will be completed."""
        if progress.completion_percentage() >= 100:
            return datetime.now()
        
        remaining_topics = progress.total_topics - len(progress.completed_topics)
        
        # Estimate 2 hours per topic average
        hours_per_topic = 2.0
        hours_needed = remaining_topics * hours_per_topic
        
        if weekly_hours > 0:
            weeks_needed = hours_needed / weekly_hours
            return datetime.now() + timedelta(weeks=weeks_needed)
        
        return datetime.now() + timedelta(weeks=52)  # Max 1 year
    
    def regenerate_with_new_constraints(self, new_constraints: SchedulingConstraints) -> None:
        """Regenerate timetable with new constraints."""
        self.constraints = new_constraints