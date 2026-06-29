# S3OS API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_token>
```

---

## Authentication Endpoints

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "password123",
  "full_name": "John Doe" // optional
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "xp": 0,
  "level": 1,
  "current_streak": 0,
  "longest_streak": 0,
  "is_active": true
}
```

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

---

## Dashboard Endpoints

### Get Dashboard Overview
```http
GET /dashboard/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "semester_progress": {
    "total_days": 120,
    "elapsed_days": 45,
    "remaining_days": 75,
    "progress_percentage": 37.5
  },
  "today_schedule": { ... },
  "current_streak": 5,
  "longest_streak": 12,
  "total_xp": 1500,
  "level": 3,
  "todays_study_hours": 3.5,
  "weekly_progress": { ... },
  "subject_progress": [ ... ],
  "pending_tasks": 3,
  "missed_tasks": 1,
  "amcat_countdown": 30
}
```

### Get Quick Stats
```http
GET /dashboard/quick-stats
Authorization: Bearer <token>
```

### Get Study Heatmap
```http
GET /dashboard/heatmap/{year}/{month}
Authorization: Bearer <token>
```

---

## Timetable Endpoints

### Generate Timetable
```http
POST /timetable/generate
Authorization: Bearer <token>
```
Generates schedules for the entire semester (120 days).

### Get Schedule for Date
```http
GET /timetable/schedule/{date}
Authorization: Bearer <token>
// date format: YYYY-MM-DD
```

### Get Schedules in Range
```http
GET /timetable/schedules?start=2025-07-14&end=2025-08-14
Authorization: Bearer <token>
```

### Complete Study Block
```http
POST /timetable/blocks/{block_id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "actual_duration": 45 // optional
}
```

**Response:**
```json
{
  "success": true,
  "xp_earned": 75,
  "total_xp": 1575,
  "leveled_up": false
}
```

### Mark Block as Missed
```http
POST /timetable/blocks/{block_id}/miss
Authorization: Bearer <token>
```

---

## Subject Endpoints

### Get All Subjects
```http
GET /subjects/
Authorization: Bearer <token>
```

### Get Subject Details
```http
GET /subjects/{subject_name}
Authorization: Bearer <token>
// e.g., /subjects/ADSA
```

### Complete Topic
```http
POST /subjects/{subject_name}/topic/{topic}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "confidence": 0.8 // 0-1 scale
}
```

### Get Weak Topics
```http
GET /subjects/{subject_name}/weak-topics
Authorization: Bearer <token>
```

---

## Analytics Endpoints

### Daily Analytics
```http
GET /analytics/daily/{date}
Authorization: Bearer <token>
```

### Weekly Analytics
```http
GET /analytics/weekly/{start_date}
Authorization: Bearer <token>
```

### Monthly Analytics
```http
GET /analytics/monthly/{year}/{month}
Authorization: Bearer <token>
```

### Semester Analytics
```http
GET /analytics/semester
Authorization: Bearer <token>
```

### Study Heatmap
```http
GET /analytics/heatmap/{year}/{month}
Authorization: Bearer <token>
```

### Subject Distribution
```http
GET /analytics/subjects/distribution
Authorization: Bearer <token>
```

### AMCAT Readiness
```http
GET /analytics/amcat/readiness
Authorization: Bearer <token>
```

### Burndown Chart
```http
GET /analytics/burndown
Authorization: Bearer <token>
```

---

## Task Endpoints

### Get Missed Tasks
```http
GET /tasks/missed
Authorization: Bearer <token>
```

### Reschedule Task
```http
POST /tasks/missed/{task_id}/reschedule
Authorization: Bearer <token>
```

### Delete Missed Task
```http
DELETE /tasks/missed/{task_id}
Authorization: Bearer <token>
```

### Pomodoro - Start
```http
POST /tasks/pomodoro/start/{block_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_type": "focus" // focus, short_break, long_break
}
```

### Pomodoro - Pause
```http
POST /tasks/pomodoro/pause/{session_id}
Authorization: Bearer <token>
```

### Pomodoro - Resume
```http
POST /tasks/pomodoro/resume/{session_id}
Authorization: Bearer <token>
```

### Pomodoro - Finish
```http
POST /tasks/pomodoro/finish/{session_id}
Authorization: Bearer <token>
```

### Pomodoro - Interrupt
```http
POST /tasks/pomodoro/interrupt/{session_id}
Authorization: Bearer <token>
```

### Get Active Pomodoro
```http
GET /tasks/pomodoro/active
Authorization: Bearer <token>
```

### Pomodoro Stats
```http
GET /tasks/pomodoro/stats
Authorization: Bearer <token>
```

---

## AMCAT Endpoints

### Get AMCAT Overview
```http
GET /amcat/
Authorization: Bearer <token>
```

### Get AMCAT Sections
```http
GET /amcat/sections
Authorization: Bearer <token>
```

### Get AMCAT Readiness
```http
GET /amcat/readiness
Authorization: Bearer <token>
```

### Get AMCAT Schedule
```http
GET /amcat/schedule
Authorization: Bearer <token>
```

### Log Practice Test
```http
POST /amcat/practice-test
Authorization: Bearer <token>
Content-Type: application/json

{
  "section": "Quantitative Aptitude",
  "score": 75,
  "total": 100
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
