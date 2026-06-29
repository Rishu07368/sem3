# S3OS - Academic Operating System

<p align="center">
  <img src="https://img.shields.io/badge/React-18-blue" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-Python-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/TypeScript-5.3-blue" alt="TypeScript">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-blue" alt="PostgreSQL">
</p>

**S3OS** is an intelligent study planning and tracking application designed specifically for Computer Science students. It combines automated scheduling, spaced repetition, analytics, and gamification to help students maximize their learning outcomes.

## Features

### 🎯 Intelligent Scheduling Engine
- **Dynamic Timetable Generation**: Automatically generates schedules for 120 days (July 14 - November 10)
- **Subject Priority System**: ADSA → COA → DBMS → Probability → Python → UHV → Soft Skills
- **Multiple Study Modes**: Normal, AMCAT (Aug 15 - Sep 15), and Exam modes
- **Adaptive Scheduling**: Considers missed tasks, upcoming exams, and confidence levels

### 📊 Analytics & Insights
- **Study Heatmaps**: GitHub-style activity visualization
- **Weekly/Monthly/Semester Reports**: Comprehensive progress tracking
- **Subject Distribution**: Time allocation across subjects
- **AMCAT Readiness Assessment**: Track your placement preparation
- **Burn-down Charts**: Visualize syllabus completion

### 🔄 Spaced Repetition System
- **SM-2 Algorithm**: Optimized revision scheduling
- **Automatic Intervals**: 1, 3, 7, 14, 30, 60, 90 days
- **Confidence Tracking**: Identify weak topics
- **Smart Rescheduling**: Never miss a revision

### 🏆 Gamification
- **XP System**: Earn experience points for every activity
- **Level Progression**: Level up as you study consistently
- **Achievements**: Unlock badges for milestones
- **Daily/Weekly Missions**: Stay motivated with goals
- **Streak Tracking**: Build consistent study habits

### 📅 Calendar Integration
- **120-Day Calendar View**: Color-coded study intensity
- **Day-by-Day Schedules**: Click any date to view your plan
- **Quick Navigation**: Jump between weeks and months

### 📚 Subject Modules
Dedicated pages for each subject with:
- Topic checklists with completion tracking
- Difficulty and importance ratings
- Weak topic identification
- Study hours tracking
- Revision count

### 🍅 Pomodoro Timer
- **Built-in Focus Timer**: Stay productive
- **XP Rewards**: Bonus points for completed sessions
- **Session History**: Track your focus patterns

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **TailwindCSS** for styling
- **React Query** for server state
- **React Router** for navigation
- **Recharts** for analytics visualizations
- **Framer Motion** for animations

### Backend
- **FastAPI** - High-performance async framework
- **SQLAlchemy 2.0** - Type-safe ORM
- **JWT Authentication** - Secure auth
- **Pydantic** - Data validation
- **Alembic** - Database migrations

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production)

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --reload --port 5000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/docs

### Using Docker

```bash
# Build and run all services
docker-compose up --build

# Stop services
docker-compose down
```

## Project Structure

```
semester3/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── config.py           # Configuration
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   │   ├── scheduling_engine.py   # Timetable generation
│   │   ├── revision_engine.py     # Spaced repetition
│   │   ├── analytics_engine.py    # Reports & insights
│   │   └── gamification.py        # XP & achievements
│   └── utils/              # Security utilities
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route pages
│   │   ├── services/       # API client
│   │   ├── contexts/       # React contexts
│   │   └── types/         # TypeScript definitions
│   └── ...
├── database/
│   └── schema.sql          # Database schema
├── docs/
│   ├── API.md              # API documentation
│   └── Architecture.md      # System design
├── docker-compose.yml      # Docker configuration
└── README.md
```

## Subject Priorities

| Subject | Priority | Difficulty | Placement Importance | Weekly Hours |
|---------|----------|------------|---------------------|--------------|
| ADSA | 1 | 9.5/10 | 10/10 | 12-15 |
| COA | 2 | 8.5/10 | 8/10 | 8-10 |
| DBMS | 3 | 7.5/10 | 9/10 | 8-10 |
| Probability | 4 | 7/10 | 6/10 | 6-8 |
| Python | 5 | 3/10 | 6/10 | 2-3 |
| UHV | 6 | 2/10 | 1/10 | 1 |
| Soft Skills | 7 | 2/10 | 2/10 | 1 |

## API Documentation

Full API documentation is available at `/docs` when the backend is running.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login and get token |
| GET | /api/v1/dashboard/ | Get dashboard overview |
| POST | /api/v1/timetable/generate | Generate full timetable |
| GET | /api/v1/subjects/ | Get all subjects |
| POST | /api/v1/subjects/{name}/topic/{topic}/complete | Mark topic done |
| GET | /api/v1/analytics/semester | Get semester analytics |
| GET | /api/v1/amcat/ | Get AMCAT overview |

## License

MIT License - Created for Chandigarh University BE Computer Science students.
