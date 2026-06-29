import {
  Clock,
  Flame,
  Star,
  Target,
  TrendingUp,
  Calendar,
  BookOpen,
  Trophy,
  Zap,
  ChevronRight,
  Play,
} from 'lucide-react';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';

// Mock data for personal use - no backend required
const mockDashboard = {
  current_streak: 5,
  longest_streak: 12,
  todays_study_hours: 3.5,
  amcat_countdown: 45,
  semester_progress: {
    progress_percentage: 35,
    remaining_days: 78,
    elapsed_days: 42,
  },
  today_schedule: {
    study_blocks: [
      { id: 1, subject: 'ADSA', topic: 'Dynamic Programming', start_time: '07:30', end_time: '08:30', duration_minutes: 60, completed: false },
      { id: 2, subject: 'DBMS', topic: 'SQL Joins', start_time: '09:30', end_time: '10:30', duration_minutes: 60, completed: true },
      { id: 3, subject: 'COA', topic: 'Cache Memory', start_time: '19:30', end_time: '21:00', duration_minutes: 90, completed: false },
    ],
  },
  subject_progress: [
    { subject: 'ADSA', completed: 12, total: 20, percentage: 60 },
    { subject: 'DBMS', completed: 5, total: 8, percentage: 62.5 },
    { subject: 'COA', completed: 4, total: 10, percentage: 40 },
    { subject: 'Probability', completed: 3, total: 8, percentage: 37.5 },
  ],
  weekly_progress: {
    total_minutes: 1260,
    days_active: 5,
    xp_earned: 450,
  },
};

export default function DashboardPage() {
  const today = new Date();
  const dashboard = mockDashboard;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome to S3OS!
          </h1>
          <p className="text-gray-400 mt-1">
            {format(today, 'EEEE, MMMM d, yyyy')}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg">
            <Star className="w-5 h-5 text-yellow-400" />
            <span className="text-white font-semibold">Level 3</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg">
            <Zap className="w-5 h-5 text-primary-400" />
            <span className="text-white font-semibold">1250 XP</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Flame}
          label="Current Streak"
          value={`${dashboard.current_streak} days`}
          color="orange"
        />
        <StatCard
          icon={Trophy}
          label="Longest Streak"
          value={`${dashboard.longest_streak} days`}
          color="yellow"
        />
        <StatCard
          icon={Clock}
          label="Today's Study"
          value={`${dashboard.todays_study_hours}h`}
          color="blue"
        />
        <StatCard
          icon={Target}
          label="AMCAT Countdown"
          value={`${dashboard.amcat_countdown} days`}
          color="purple"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Schedule */}
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary-400" />
              Today's Schedule
            </h2>
            <Link
              to="/calendar"
              className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View Calendar <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          {dashboard.today_schedule.study_blocks?.length ? (
            <div className="space-y-3">
              {dashboard.today_schedule.study_blocks.map((block: any, index: number) => (
                <div
                  key={block.id || index}
                  className={`p-4 rounded-lg border ${
                    block.completed
                      ? 'bg-green-900/30 border-green-700'
                      : 'bg-gray-700/50 border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          block.completed ? 'bg-green-500' : 'bg-gray-500'
                        }`}
                      />
                      <div>
                        <p className="text-white font-medium">{block.subject}</p>
                        <p className="text-sm text-gray-400">{block.topic}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-300">
                        {block.start_time} - {block.end_time}
                      </p>
                      <p className="text-xs text-gray-500">
                        {block.duration_minutes} min
                      </p>
                    </div>
                  </div>
                  {!block.completed && (
                    <button className="mt-3 w-full btn btn-primary flex items-center justify-center gap-2">
                      <Play className="w-4 h-4" /> Start Study
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No study blocks scheduled for today</p>
              <Link to="/calendar" className="text-primary-400 hover:underline mt-2 inline-block">
                View your calendar
              </Link>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Semester Progress */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              Semester Progress
            </h2>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Overall Progress</span>
                  <span className="text-white">
                    {dashboard.semester_progress.progress_percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 rounded-full transition-all duration-500"
                    style={{ width: `${dashboard.semester_progress.progress_percentage}%` }}
                  />
                </div>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Days Remaining</span>
                <span className="text-white">
                  {dashboard.semester_progress.remaining_days}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Days Elapsed</span>
                <span className="text-white">
                  {dashboard.semester_progress.elapsed_days}
                </span>
              </div>
            </div>
          </div>

          {/* Subject Progress */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-400" />
              Subject Progress
            </h2>
            <div className="space-y-3">
              {dashboard.subject_progress.slice(0, 5).map((subject) => (
                <div key={subject.subject}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">{subject.subject}</span>
                    <span className="text-gray-400">
                      {subject.completed}/{subject.total}
                    </span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 rounded-full transition-all duration-500"
                      style={{ width: `${subject.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link
                to="/calendar"
                className="flex items-center gap-3 p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-colors"
              >
                <Calendar className="w-5 h-5 text-primary-400" />
                <span className="text-gray-300">View Calendar</span>
              </Link>
              <Link
                to="/analytics"
                className="flex items-center gap-3 p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-colors"
              >
                <TrendingUp className="w-5 h-5 text-green-400" />
                <span className="text-gray-300">View Analytics</span>
              </Link>
              <Link
                to="/amcat"
                className="flex items-center gap-3 p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-colors"
              >
                <Target className="w-5 h-5 text-purple-400" />
                <span className="text-gray-300">AMCAT Prep</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Weekly Progress */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-400" />
          This Week
        </h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <p className="text-2xl font-bold text-primary-400">
              {(dashboard.weekly_progress.total_minutes / 60).toFixed(1)}h
            </p>
            <p className="text-sm text-gray-400">Study Hours</p>
          </div>
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <p className="text-2xl font-bold text-green-400">
              {dashboard.weekly_progress.days_active}
            </p>
            <p className="text-sm text-gray-400">Days Active</p>
          </div>
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <p className="text-2xl font-bold text-yellow-400">
              {dashboard.weekly_progress.xp_earned}
            </p>
            <p className="text-sm text-gray-400">XP Earned</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  color: 'blue' | 'orange' | 'yellow' | 'purple' | 'green';
}) {
  const colors = {
    blue: 'bg-blue-500/20 text-blue-400',
    orange: 'bg-orange-500/20 text-orange-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    purple: 'bg-purple-500/20 text-purple-400',
    green: 'bg-green-500/20 text-green-400',
  };

  return (
    <div className="card p-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}
