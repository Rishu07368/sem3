import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
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

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.getDashboard(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500" />
      </div>
    );
  }

  const today = new Date();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.full_name || user?.username}!
          </h1>
          <p className="text-gray-400 mt-1">
            {format(today, 'EEEE, MMMM d, yyyy')}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg">
            <Star className="w-5 h-5 text-yellow-400" />
            <span className="text-white font-semibold">Level {user?.level || 1}</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg">
            <Zap className="w-5 h-5 text-primary-400" />
            <span className="text-white font-semibold">{user?.xp || 0} XP</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Flame}
          label="Current Streak"
          value={`${dashboard?.current_streak || 0} days`}
          color="orange"
        />
        <StatCard
          icon={Trophy}
          label="Longest Streak"
          value={`${dashboard?.longest_streak || 0} days`}
          color="yellow"
        />
        <StatCard
          icon={Clock}
          label="Today's Study"
          value={`${dashboard?.todays_study_hours?.toFixed(1) || 0}h`}
          color="blue"
        />
        <StatCard
          icon={Target}
          label="AMCAT Countdown"
          value={`${dashboard?.amcat_countdown || 0} days`}
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

          {dashboard?.today_schedule?.study_blocks?.length ? (
            <div className="space-y-3">
              {dashboard.today_schedule.study_blocks.map((block, index) => (
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
                    {dashboard?.semester_progress?.progress_percentage?.toFixed(1) || 0}%
                  </span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 rounded-full transition-all duration-500"
                    style={{ width: `${dashboard?.semester_progress?.progress_percentage || 0}%` }}
                  />
                </div>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Days Remaining</span>
                <span className="text-white">
                  {dashboard?.semester_progress?.remaining_days || 0}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Days Elapsed</span>
                <span className="text-white">
                  {dashboard?.semester_progress?.elapsed_days || 0}
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
              {dashboard?.subject_progress?.slice(0, 5).map((subject) => (
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
                      style={{ width: `${subject.percentage || 0}%` }}
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
              {(dashboard?.weekly_progress?.total_minutes / 60)?.toFixed(1) || 0}h
            </p>
            <p className="text-sm text-gray-400">Study Hours</p>
          </div>
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <p className="text-2xl font-bold text-green-400">
              {dashboard?.weekly_progress?.days_active || 0}
            </p>
            <p className="text-sm text-gray-400">Days Active</p>
          </div>
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <p className="text-2xl font-bold text-yellow-400">
              {dashboard?.weekly_progress?.xp_earned || 0}
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
