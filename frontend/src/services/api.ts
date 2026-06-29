import type {
  User,
  DailySchedule,
  Subject,
  DashboardData,
  WeeklyAnalytics,
  HeatmapDay,
  Achievement,
  DailyMission,
  AMCATOverview,
  AMCATSection,
  PomodoroSession,
  MissedTask,
  TokenResponse,
  LoginRequest,
  RegisterRequest,
  StudyBlock,
} from '@/types';

const API_BASE = '/api/v1';

class ApiService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Auth
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(data: RegisterRequest): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    this.clearToken();
  }

  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    return this.request<DashboardData>('/dashboard/');
  }

  async getQuickStats(): Promise<{
    today_study_minutes: number;
    week_study_minutes: number;
    current_streak: number;
    xp: number;
    level: number;
  }> {
    return this.request('/dashboard/quick-stats');
  }

  async getHeatmap(year: number, month: number): Promise<{ heatmap: HeatmapDay[] }> {
    return this.request(`/dashboard/heatmap/${year}/${month}`);
  }

  // Timetable
  async generateTimetable(): Promise<{ success: boolean; message: string }> {
    return this.request('/timetable/generate', { method: 'POST' });
  }

  async getSchedule(date: string): Promise<DailySchedule> {
    return this.request<DailySchedule>(`/timetable/schedule/${date}`);
  }

  async getSchedules(start?: string, end?: string): Promise<{ schedules: DailySchedule[]; count: number }> {
    const params = new URLSearchParams();
    if (start) params.append('start', start);
    if (end) params.append('end', end);
    return this.request(`/timetable/schedules?${params}`);
  }

  async getBlock(blockId: number): Promise<StudyBlock> {
    return this.request<StudyBlock>(`/timetable/blocks/${blockId}`);
  }

  async completeBlock(
    blockId: number,
    actualDuration?: number
  ): Promise<{ success: boolean; xp_earned: number; total_xp: number; leveled_up: boolean }> {
    return this.request(`/timetable/blocks/${blockId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ actual_duration: actualDuration }),
    });
  }

  async missBlock(blockId: number): Promise<{ success: boolean; message: string }> {
    return this.request(`/timetable/blocks/${blockId}/miss`, { method: 'POST' });
  }

  // Subjects
  async getSubjects(): Promise<{ subjects: Subject[] }> {
    return this.request('/subjects/');
  }

  async getSubject(name: string): Promise<Subject> {
    return this.request<Subject>(`/subjects/${encodeURIComponent(name)}`);
  }

  async completeTopic(
    subjectName: string,
    topic: string,
    confidence: number = 0.7
  ): Promise<{ success: boolean; completed_topics: string[]; completion_percentage: number }> {
    return this.request(`/subjects/${encodeURIComponent(subjectName)}/topic/${encodeURIComponent(topic)}/complete`, {
      method: 'POST',
      body: JSON.stringify({ confidence }),
    });
  }

  // Analytics
  async getDailyAnalytics(date: string): Promise<{
    date: string;
    total_study_minutes: number;
    completed_study_minutes: number;
    blocks_completed: number;
    blocks_total: number;
    completion_rate: number;
    xp_earned: number;
  }> {
    return this.request(`/analytics/daily/${date}`);
  }

  async getWeeklyAnalytics(startDate: string): Promise<WeeklyAnalytics> {
    return this.request<WeeklyAnalytics>(`/analytics/weekly/${startDate}`);
  }

  async getMonthlyAnalytics(year: number, month: number): Promise<{
    year: number;
    month: number;
    total_study_hours: number;
    total_xp: number;
    days_active: number;
  }> {
    return this.request(`/analytics/monthly/${year}/${month}`);
  }

  async getSemesterAnalytics(): Promise<{
    total_study_hours: number;
    total_xp: number;
    level: number;
    tasks_completed: number;
    tasks_missed: number;
    completion_rate: number;
    current_streak: number;
    longest_streak: number;
  }> {
    return this.request('/analytics/semester');
  }

  // Tasks
  async getMissedTasks(): Promise<{ tasks: MissedTask[] }> {
    return this.request('/tasks/missed');
  }

  async rescheduleTask(taskId: number): Promise<{ success: boolean }> {
    return this.request(`/tasks/missed/${taskId}/reschedule`, { method: 'POST' });
  }

  // Pomodoro
  async startPomodoro(blockId: number, sessionType: string = 'focus'): Promise<{
    session_id: number;
    start_time: string;
    session_type: string;
  }> {
    return this.request(`/tasks/pomodoro/start/${blockId}`, {
      method: 'POST',
      body: JSON.stringify({ session_type: sessionType }),
    });
  }

  async pausePomodoro(sessionId: number): Promise<{ success: boolean; status: string }> {
    return this.request(`/tasks/pomodoro/pause/${sessionId}`, { method: 'POST' });
  }

  async resumePomodoro(sessionId: number): Promise<{ success: boolean; status: string }> {
    return this.request(`/tasks/pomodoro/resume/${sessionId}`, { method: 'POST' });
  }

  async finishPomodoro(sessionId: number): Promise<{
    success: boolean;
    duration_minutes: number;
    xp_earned: number;
  }> {
    return this.request(`/tasks/pomodoro/finish/${sessionId}`, { method: 'POST' });
  }

  async interruptPomodoro(sessionId: number): Promise<{ success: boolean; xp_lost: number }> {
    return this.request(`/tasks/pomodoro/interrupt/${sessionId}`, { method: 'POST' });
  }

  async getActivePomodoro(): Promise<{ active: boolean; session?: PomodoroSession }> {
    return this.request('/tasks/pomodoro/active');
  }

  // AMCAT
  async getAMCATOverview(): Promise<AMCATOverview> {
    return this.request('/amcat/');
  }

  async getAMCATSections(): Promise<{ sections: AMCATSection[] }> {
    return this.request('/amcat/sections');
  }

  async getAMCATReadiness(): Promise<{
    overall_readiness: number;
    status: string;
  }> {
    return this.request('/amcat/readiness');
  }

  async logPracticeTest(
    section: string,
    score: number,
    total: number = 100
  ): Promise<{ success: boolean; percentage: number; xp_earned: number }> {
    return this.request('/amcat/practice-test', {
      method: 'POST',
      body: JSON.stringify({ section, score, total }),
    });
  }
}

export const api = new ApiService();
