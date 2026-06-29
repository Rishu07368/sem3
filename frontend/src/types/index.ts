// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  xp: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  is_active: boolean;
}

// Study block types
export interface StudyBlock {
  id: number;
  user_id: number;
  schedule_id: number | null;
  subject: string;
  topic: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  is_amcat: boolean;
  is_revision: boolean;
  order_index: number;
  completed: boolean;
  actual_start_time: string | null;
  actual_end_time: string | null;
  actual_duration_minutes: number | null;
  xp_earned: number;
  pomodoro_sessions: number;
  interrupted: number;
}

export interface FixedTimeSlot {
  id: number;
  start_time: string;
  end_time: string;
  activity: string;
  flexible_end: string | null;
}

export interface DailySchedule {
  id: number;
  user_id: number;
  date: string;
  mode: 'normal' | 'amcat' | 'exam';
  total_study_minutes: number;
  completion_percentage: number;
  mood_rating: number | null;
  energy_rating: number | null;
  notes: string | null;
  study_blocks: StudyBlock[];
  fixed_slots: FixedTimeSlot[];
}

// Subject types
export interface Subject {
  id: number;
  name: string;
  priority: number;
  difficulty: number;
  placement_importance: number;
  target_hours_min: number;
  target_hours_max: number;
  topics: string[];
  topics_count: number;
  completed_topics: string[];
  confidence_scores: Record<string, number>;
  weak_topics: string[];
  completion_percentage: number;
  total_study_hours: number;
  revision_count: number;
  last_studied: string | null;
}

export interface SubjectProgress {
  id: number;
  user_id: number;
  subject_name: string;
  total_topics: number;
  completed_topics: string[];
  completion_percentage: number;
  confidence_scores: Record<string, number>;
  weak_topics: string[];
  total_study_hours: number;
  revision_count: number;
  last_studied: string | null;
}

// Analytics types
export interface DailyAnalytics {
  date: string;
  total_study_minutes: number;
  completed_study_minutes: number;
  blocks_completed: number;
  blocks_total: number;
  completion_rate: number;
  mood_rating: number | null;
  energy_rating: number | null;
  xp_earned: number;
  tasks_completed: number;
  tasks_missed: number;
}

export interface WeeklyAnalytics {
  start_date: string;
  end_date: string;
  total_study_minutes: number;
  total_study_hours: number;
  average_daily_hours: number;
  total_xp: number;
  tasks_completed: number;
  tasks_missed: number;
  daily_breakdown: Array<{
    date: string;
    minutes: number;
    xp: number;
  }>;
  subject_distribution: Record<string, number>;
}

export interface HeatmapDay {
  date: string;
  minutes: number;
  intensity: number;
  weekday: number;
}

// Dashboard types
export interface DashboardData {
  semester_progress: {
    total_days: number;
    elapsed_days: number;
    remaining_days: number;
    progress_percentage: number;
  };
  today_schedule: DailySchedule | null;
  current_streak: number;
  longest_streak: number;
  total_xp: number;
  level: number;
  todays_study_hours: number;
  weekly_progress: {
    total_minutes: number;
    days_active: number;
    xp_earned: number;
  };
  subject_progress: Array<{
    subject: string;
    completed: number;
    total: number;
    percentage: number;
    study_hours: number;
  }>;
  pending_tasks: number;
  missed_tasks: number;
  amcat_countdown: number;
}

// Gamification types
export interface Achievement {
  id: number;
  code: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  xp_reward: number;
  earned_at?: string;
}

export interface DailyMission {
  id: string;
  title: string;
  description: string;
  target: number;
  progress: number;
  xp_reward: number;
  completed: boolean;
}

// AMCAT types
export interface AMCATSection {
  id: string;
  name: string;
  topics: string[];
  hours_target: number;
  hours_completed: number;
  topics_completed: number;
  topics_total: number;
  percentage: number;
  icon: string;
}

export interface AMCATOverview {
  in_amcat_period: boolean;
  amcat_start: string;
  amcat_end: string;
  days_until_amcat: number;
  total_blocks: number;
  completed_blocks: number;
  completion_percentage: number;
  readiness: {
    amcat_practice_completed: number;
    amcat_practice_total: number;
    amcat_practice_percentage: number;
    core_subject_progress: Record<string, number>;
    avg_core_progress: number;
    overall_readiness: number;
    status: string;
  };
}

// Pomodoro types
export interface PomodoroSession {
  id: number;
  user_id: number;
  study_block_id: number | null;
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;
  status: 'in_progress' | 'paused' | 'completed' | 'interrupted';
  session_type: 'focus' | 'short_break' | 'long_break';
  xp_earned: number;
}

// Missed task types
export interface MissedTask {
  id: number;
  original_date: string;
  subject: string;
  topic: string;
  rescheduled: boolean;
  rescheduled_to: string | null;
}

// Notification types
export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
