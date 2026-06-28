# Daily Timetable Engine

An intelligent study planning and tracking application for BE Computer Science students at Chandigarh University.

## Features

### Core Features
- **Intelligent Scheduling Engine**: Automatically generates daily timetables based on configurable constraints
- **120-Day Coverage**: Complete schedule from July 14 to November 10, 2025
- **Fixed Daily Activities**: Sleep, breakfast, college, gym, dinner - all configurable
- **Dynamic Study Blocks**: Morning revision, evening study, night deep-work sessions

### Subject Priorities
1. ADSA (12-15 hrs/week) - Highest placement priority
2. COA (8-10 hrs/week) - Concept-heavy core CS
3. DBMS (8-10 hrs/week) - SQL and database fundamentals
4. Probability (6-8 hrs/week) - Engineering mathematics
5. Python (2-3 hrs/week) - Revision only
6. UHV (1 hr/week) - Theory subject
7. Soft Skills (1 hr/week) - Communication & personality

### Study Modes
- **Normal Mode**: Standard semester schedule
- **AMCAT Mode** (Aug 15 - Sep 15): Increased aptitude study time
- **Exam Mode** (3 weeks before exams): Revision-focused

### Interactive Features
- **Daily Page**: Timeline, tasks, progress bars, pomodoro timer
- **Calendar View**: Color-coded days (green/yellow/red/blue/grey)
- **Smart Rescheduling**: Missed tasks automatically moved to future slots
- **Analytics Dashboard**: Daily, weekly, monthly, semester reports
- **Mood & Energy Tracking**: Daily check-ins for self-awareness

### Technical Highlights
- **Scheduling Engine**: Reusable, extensible, maintainable
- **Configuration-Driven**: Change constraints, regenerate entire timetable
- **SQLite Database**: Persistent storage for schedules, progress, analytics
- **REST API**: Full backend for mobile apps and integrations

## Architecture

```
/workspace/project
├── backend/
│   ├── app.py                 # Flask application factory
│   ├── models/
│   │   └── database.py        # SQLAlchemy models
│   ├── routes/
│   │   └── api.py             # REST API endpoints
│   └── services/
│       ├── scheduling_engine.py  # Core scheduling logic
│       └── subjects.py        # Subject definitions
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main application
│   │   ├── pages/
│   │   │   ├── DailyPage.jsx     # Daily timetable view
│   │   │   ├── CalendarPage.jsx  # Calendar view
│   │   │   ├── AnalyticsPage.jsx # Analytics dashboard
│   │   │   └── SettingsPage.jsx  # Configuration
│   │   └── context/
│   │       └── AppContext.jsx    # React context
│   └── build/                 # Production build
└── README.md
```

## Running the Application

### Start Backend
```bash
cd /workspace/project/backend
pip install -r requirements.txt
python app.py
```

### Start Frontend (Development)
```bash
cd /workspace/project/frontend
npm install
npm run dev
```

### Production Build
```bash
cd /workspace/project/frontend
npm run build
```

Then access at `http://localhost:5000`

## API Endpoints

### Timetable Generation
- `POST /api/generate` - Generate complete timetable
- `GET /api/schedule/<date>` - Get schedule for specific date
- `GET /api/schedules?start=&end=` - Get schedules in range
- `POST /api/regenerate` - Regenerate with new constraints

### Study Blocks
- `GET /api/blocks/<id>` - Get study block details
- `POST /api/blocks/<id>/complete` - Mark block as completed
- `POST /api/blocks/<id>/miss` - Mark block as missed
- `POST /api/blocks/<id>/reschedule` - Reschedule to new date

### Pomodoro Timer
- `POST /api/pomodoro/start/<block_id>` - Start pomodoro
- `POST /api/pomodoro/pause/<session_id>` - Pause session
- `POST /api/pomodoro/resume/<session_id>` - Resume session
- `POST /api/pomodoro/finish/<session_id>` - Finish session
- `POST /api/pomodoro/interrupt/<session_id>` - Interrupt session

### Analytics
- `GET /api/analytics/daily/<date>` - Daily analytics
- `GET /api/analytics/weekly/<start_date>` - Weekly analytics
- `GET /api/analytics/monthly/<year>/<month>` - Monthly analytics
- `GET /api/analytics/semester` - Semester analytics
- `GET /api/analytics/streaks` - Streak information

### Configuration
- `GET /api/config` - Get all configuration
- `GET /api/config/<key>` - Get specific value
- `PUT /api/config/<key>` - Update value

### Calendar
- `GET /api/calendar?year=&month=` - Get calendar data for month

## Configuration Options

The scheduling engine is fully configurable:

```python
SchedulingConstraints(
    start_date=datetime(2025, 7, 14),
    end_date=datetime(2025, 11, 10),
    
    # Fixed activities (all configurable)
    sleep_start="23:30",
    sleep_end="07:00",
    college_start="09:30",
    college_end="16:30",
    gym_start="17:30",
    gym_end="19:00",
    
    # Mode dates
    amcat_start_date=datetime(2025, 8, 15),
    amcat_end_date=datetime(2025, 9, 15),
    exam_start_date=datetime(2025, 11, 1),
    
    # Study time allocation
    total_available_study_hours=30.0,
)
```

## Subject Syllabi

### ADSA (Highest Priority)
Arrays, Strings, Recursion, Searching, Sorting, Linked Lists, Stacks, Queues, Trees, BST, AVL Trees, Heaps, Hashing, Graphs (BFS/DFS/Shortest Paths), Greedy, Backtracking, Dynamic Programming

### COA
Number Systems, Boolean Algebra, CPU Organization, Registers, Instruction Cycle, Memory Hierarchy, Cache Memory, Pipelining, Interrupts, I/O Organization

### DBMS
SQL Queries, Joins, Normalization, Transactions, Indexes, ER Diagrams, Constraints, Practice Query Solving

### Probability & Statistics
Probability Basics, Conditional Probability, Bayes Theorem, Random Variables, Probability Distributions, Mean/Variance/StdDev, Sampling, Correlation and Regression

## License

MIT License - Created for Chandigarh University BE Computer Science students.