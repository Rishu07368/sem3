# S3OS Architecture Documentation

## Overview

S3OS (Semester 3 Operating System) is an intelligent study planning and tracking application built for Computer Science students. It provides automated scheduling, spaced repetition, analytics, and gamification to optimize learning outcomes.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │Dashboard│ │Calendar │ │Subjects │ │AMCAT    │ │Analytics│ │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ │
│       └────────────┴────────────┴────────────┴────────────┘      │
│                              │                                   │
│                    React Query + Context                          │
└──────────────────────────────┼───────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────┼───────────────────────────────────┐
│                    Backend (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      API Routes                              ││
│  │  auth │ dashboard │ timetable │ subjects │ analytics │ amcat││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Services Layer                           ││
│  │  Scheduling │ Revision │ Analytics │ Gamification │ Notifs ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Data Layer (SQLAlchemy)                 ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────────┼───────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)                   │
└──────────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI (async, high-performance)
- **ORM**: SQLAlchemy 2.0 (type-safe, modern)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Validation**: Pydantic v2

### Directory Structure
```
backend/
├── app.py                 # Application entry point
├── config.py              # Configuration management
├── database.py            # Database connection
├── models/
│   └── database.py        # SQLAlchemy models
├── routes/
│   ├── auth.py            # Authentication routes
│   ├── dashboard.py       # Dashboard data
│   ├── timetable.py        # Schedule management
│   ├── subjects.py        # Subject progress
│   ├── analytics.py       # Analytics endpoints
│   ├── tasks.py           # Tasks & Pomodoro
│   └── amcat.py           # AMCAT preparation
├── services/
│   ├── scheduling_engine.py  # Intelligent scheduling
│   ├── revision_engine.py   # Spaced repetition
│   ├── analytics_engine.py  # Analytics calculations
│   ├── gamification.py      # XP & achievements
│   └── notification_service.py
├── middleware/
├── utils/
│   └── security.py          # Auth utilities
├── tests/
└── migrations/
```

### Service Layer

#### Scheduling Engine
The core component that generates daily timetables dynamically:

```python
class SchedulingEngine:
    def generate_daily_schedule(date) -> DailySchedule
    def generate_timetable() -> List[DailySchedule]
    def get_mode_for_date(date) -> StudyMode  # NORMAL, AMCAT, EXAM
    def get_study_hours_distribution(mode) -> Dict[str, float]
```

**Features:**
- Dynamic schedule generation based on constraints
- Subject priority-based allocation
- AMCAT mode with increased aptitude focus
- Exam mode with weak subject prioritization
- Weekend vs weekday differentiation

#### Revision Engine
Implements spaced repetition using SM-2 algorithm:

```python
class RevisionEngine:
    def schedule_revision(subject, topic, confidence)
    def get_due_revisions(date) -> List[RevisionSession]
    def complete_revision(revision_id, quality)  # quality 0-5
```

**Intervals:** 1, 3, 7, 14, 30, 60, 90 days

#### Analytics Engine
Comprehensive analytics and reporting:

```python
class AnalyticsEngine:
    def get_daily_analytics(date)
    def get_weekly_analytics(start_date)
    def get_monthly_analytics(year, month)
    def get_semester_analytics()
    def get_study_heatmap(year, month)
    def get_amcat_readiness()
```

#### Gamification Service
XP, levels, achievements, and missions:

```python
class GamificationService:
    def add_xp(amount, reason) -> Dict
    def award_xp_for_block_complete(block) -> Dict
    def check_and_award_achievements() -> List[Achievement]
    def update_streak() -> Dict
    def get_daily_missions() -> List[Mission]
```

### Data Models

#### Core Models
- **User**: Authentication and gamification state
- **DailySchedule**: Daily schedule with fixed slots and study blocks
- **StudyBlock**: Individual study sessions
- **SubjectProgress**: Per-subject progress tracking

#### Supporting Models
- **RevisionSession**: Spaced repetition data
- **PomodoroSession**: Pomodoro timer sessions
- **DailyMetrics**: Daily aggregations
- **Achievement/UserAchievement**: Gamification
- **Notification**: User notifications

## Frontend Architecture

### Technology Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: React Query + Context
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **Charts**: Recharts

### Directory Structure
```
frontend/src/
├── main.tsx              # Entry point
├── App.tsx               # Root component with routing
├── index.css             # Global styles
├── types/
│   └── index.ts          # TypeScript interfaces
├── services/
│   └── api.ts             # API client
├── contexts/
│   └── AuthContext.tsx    # Authentication context
├── components/
│   └── common/
│       └── Layout.tsx      # Main layout with sidebar
└── pages/
    ├── Login.tsx
    ├── Dashboard.tsx
    ├── Calendar.tsx
    ├── ADSA.tsx
    ├── DBMS.tsx
    ├── COA.tsx
    ├── Probability.tsx
    ├── AMCAT.tsx
    ├── Analytics.tsx
    └── Settings.tsx
```

### Key Patterns

#### API Integration
```typescript
// Using React Query
const { data, isLoading } = useQuery({
  queryKey: ['dashboard'],
  queryFn: () => api.getDashboard(),
});
```

#### Protected Routes
```typescript
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" />;
  return <>{children}</>;
}
```

## Database Schema

### Key Relationships
```
User (1) ─── (N) DailySchedule
User (1) ─── (N) StudyBlock
User (1) ─── (N) SubjectProgress
User (1) ─── (N) DailyMetrics
User (1) ─── (N) Achievement
StudyBlock (1) ─── (N) PomodoroSession
StudyBlock (1) ─── (N) RevisionSession
```

### Indexes
- `daily_schedules(user_id, date)` - Quick schedule lookup
- `study_blocks(user_id)` - User's study blocks
- `daily_metrics(user_id, date)` - Analytics queries
- `revision_sessions(user_id, next_revision_date)` - Due revisions

## Deployment

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production (Docker)
```bash
docker-compose up --build
```

### Database Migration
For production, use Alembic:
```bash
alembic upgrade head
```

## Security Considerations

1. **Authentication**: JWT tokens with 7-day expiry
2. **Password**: bcrypt hashing (cost factor 12)
3. **CORS**: Configurable origins
4. **Input Validation**: Pydantic schemas
5. **SQL Injection**: ORM (SQLAlchemy) prevents this
6. **XSS**: React's built-in escaping

## Performance Optimizations

1. **Database Indexes**: On frequently queried columns
2. **React Query**: Caching and background refetching
3. **Connection Pooling**: SQLAlchemy connection pool
4. **Lazy Loading**: Route-based code splitting
5. **Optimistic Updates**: For better UX

## Future Enhancements

1. **WebSocket Support**: Real-time notifications
2. **Mobile App**: React Native wrapper
3. **AI Suggestions**: ML-based study recommendations
4. **Calendar Integration**: Google/Outlook sync
5. **Export/Import**: Data portability
6. **Team Study**: Shared study sessions
