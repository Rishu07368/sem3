-- S3OS Database Schema
-- PostgreSQL compatible

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily Schedules table
CREATE TABLE daily_schedules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    mode VARCHAR(20) DEFAULT 'normal',
    total_study_minutes INTEGER DEFAULT 0,
    completion_percentage FLOAT DEFAULT 0.0,
    mood_rating INTEGER,
    energy_rating INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Fixed Time Slots table
CREATE TABLE fixed_time_slots (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL REFERENCES daily_schedules(id) ON DELETE CASCADE,
    start_time VARCHAR(5) NOT NULL,
    end_time VARCHAR(5) NOT NULL,
    activity VARCHAR(100) NOT NULL,
    flexible_end VARCHAR(5)
);

-- Study Blocks table
CREATE TABLE study_blocks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    schedule_id INTEGER REFERENCES daily_schedules(id) ON DELETE SET NULL,
    subject VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    start_time VARCHAR(5) NOT NULL,
    end_time VARCHAR(5) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    is_amcat BOOLEAN DEFAULT FALSE,
    is_revision BOOLEAN DEFAULT FALSE,
    order_index INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    actual_duration_minutes INTEGER,
    xp_earned INTEGER DEFAULT 0,
    pomodoro_sessions INTEGER DEFAULT 0,
    interrupted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    priority INTEGER DEFAULT 1,
    difficulty FLOAT DEFAULT 5.0,
    placement_importance FLOAT DEFAULT 5.0,
    target_hours_min FLOAT DEFAULT 1.0,
    target_hours_max FLOAT DEFAULT 2.0,
    is_amcat_subject BOOLEAN DEFAULT FALSE,
    topics TEXT DEFAULT '[]'
);

-- Subject Progress table
CREATE TABLE subject_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_name VARCHAR(100) NOT NULL,
    total_topics INTEGER DEFAULT 0,
    completed_topics TEXT DEFAULT '[]',
    confidence_scores TEXT DEFAULT '{}',
    weak_topics TEXT DEFAULT '[]',
    total_study_hours FLOAT DEFAULT 0.0,
    revision_count INTEGER DEFAULT 0,
    last_studied DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, subject_name)
);

-- Revision Sessions table (for spaced repetition)
CREATE TABLE revision_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    study_block_id INTEGER REFERENCES study_blocks(id) ON DELETE SET NULL,
    subject VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    interval INTEGER DEFAULT 1,
    next_revision_date DATE NOT NULL,
    repetitions INTEGER DEFAULT 0,
    ease_factor FLOAT DEFAULT 2.5,
    last_reviewed DATE,
    confidence FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Missed Tasks table
CREATE TABLE missed_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_date DATE NOT NULL,
    subject VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    rescheduled BOOLEAN DEFAULT FALSE,
    rescheduled_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pomodoro Sessions table
CREATE TABLE pomodoro_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    study_block_id INTEGER REFERENCES study_blocks(id) ON DELETE SET NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'in_progress',
    session_type VARCHAR(20) DEFAULT 'focus',
    xp_earned INTEGER DEFAULT 0
);

-- Daily Metrics table
CREATE TABLE daily_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL UNIQUE,
    total_study_minutes INTEGER DEFAULT 0,
    productive_minutes INTEGER DEFAULT 0,
    distraction_minutes INTEGER DEFAULT 0,
    subject_minutes TEXT DEFAULT '{}',
    tasks_completed INTEGER DEFAULT 0,
    tasks_missed INTEGER DEFAULT 0,
    tasks_rescheduled INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    streak_count INTEGER DEFAULT 0,
    mood_rating INTEGER,
    energy_rating INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievements table
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    icon VARCHAR(50) DEFAULT 'trophy',
    category VARCHAR(50) DEFAULT 'general',
    requirement_type VARCHAR(50) DEFAULT 'count',
    requirement_value INTEGER DEFAULT 1
);

-- User Achievements table
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id)
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration table
CREATE TABLE configuration (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Preferences table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    UNIQUE(user_id, key)
);

-- Indexes
CREATE INDEX idx_daily_schedules_user_date ON daily_schedules(user_id, date);
CREATE INDEX idx_study_blocks_user ON study_blocks(user_id);
CREATE INDEX idx_study_blocks_schedule ON study_blocks(schedule_id);
CREATE INDEX idx_daily_metrics_user_date ON daily_metrics(user_id, date);
CREATE INDEX idx_revision_sessions_user_date ON revision_sessions(user_id, next_revision_date);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- Insert default subjects
INSERT INTO subjects (name, priority, difficulty, placement_importance, target_hours_min, target_hours_max, topics) VALUES
('ADSA', 1, 9.5, 10.0, 12.0, 15.0, '["Arrays", "Strings", "Recursion", "Searching", "Sorting", "Linked Lists", "Stacks", "Queues", "Trees", "Binary Search Trees", "AVL Trees", "Heaps", "Hashing", "Graphs - BFS", "Graphs - DFS", "Graphs - Shortest Paths", "Greedy Algorithms", "Backtracking", "Dynamic Programming", "Dynamic Programming Advanced"]'),
('COA', 2, 8.5, 8.0, 8.0, 10.0, '["Number Systems", "Boolean Algebra", "CPU Organization", "Registers", "Instruction Cycle", "Memory Hierarchy", "Cache Memory", "Pipelining", "Interrupts", "Input/Output Organization"]'),
('DBMS', 3, 7.5, 9.0, 8.0, 10.0, '["SQL Queries", "Joins", "Normalization", "Transactions", "Indexes", "ER Diagrams", "Constraints", "Practice Query Solving"]'),
('Probability', 4, 7.0, 6.0, 6.0, 8.0, '["Probability Basics", "Conditional Probability", "Bayes Theorem", "Random Variables", "Probability Distributions", "Mean, Variance, Std Dev", "Sampling", "Correlation and Regression"]'),
('Python', 5, 3.0, 6.0, 2.0, 3.0, '["Syntax Revision", "Data Structures", "Functions", "OOP Concepts", "File Handling", "Problem Solving"]'),
('UHV', 6, 2.0, 1.0, 1.0, 1.0, '["Ethics and Values", "Self Awareness", "Teamwork", "Communication"]'),
('Soft Skills', 7, 2.0, 2.0, 1.0, 1.0, '["Resume Building", "Interview Preparation", "Body Language", "Presentation Skills", "Group Discussion"]');
