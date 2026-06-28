import React, { useState, useEffect, useCallback } from 'react';
import { format, subDays, startOfWeek, addDays } from 'date-fns';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  TrendingUp, Target, Flame, Award, Calendar, Clock, BookOpen,
  CheckCircle, AlertCircle, ArrowUp, ArrowDown
} from 'lucide-react';
import { API_BASE } from '../App';

const COLORS = ['#8b5cf6', '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState('daily');
  const [dailyData, setDailyData] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [semesterData, setSemesterData] = useState(null);
  const [streakData, setStreakData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAllData = useCallback(async () => {
    try {
      setIsLoading(true);
      const today = new Date();
      
      // Fetch different analytics
      const [dailyRes, weeklyRes, monthlyRes, semesterRes, streakRes] = await Promise.all([
        fetch(`${API_BASE}/analytics/daily/${format(today, 'yyyy-MM-dd')}`),
        fetch(`${API_BASE}/analytics/weekly/${format(subDays(today, 6), 'yyyy-MM-dd')}`),
        fetch(`${API_BASE}/analytics/monthly/${today.getFullYear()}/${today.getMonth() + 1}`),
        fetch(`${API_BASE}/analytics/semester`),
        fetch(`${API_BASE}/analytics/streaks`),
      ]);

      const [daily, weekly, monthly, semester, streaks] = await Promise.all([
        dailyRes.json(),
        weeklyRes.json(),
        monthlyRes.json(),
        semesterRes.json(),
        streakRes.json(),
      ]);

      setDailyData(daily);
      setWeeklyData(weekly);
      setMonthlyData(monthly);
      setSemesterData(semester);
      setStreakData(streaks);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const tabs = [
    { id: 'daily', label: 'Daily', icon: Clock },
    { id: 'weekly', label: 'Weekly', icon: Calendar },
    { id: 'monthly', label: 'Monthly', icon: TrendingUp },
    { id: 'semester', label: 'Semester', icon: Award },
  ];

  // Prepare chart data
  const weeklyChartData = weeklyData?.daily_metrics?.map(d => ({
    date: format(new Date(d.date), 'EEE'),
    minutes: d.total_study_minutes,
    xp: d.xp_earned,
    completed: d.tasks_completed,
  })) || [];

  const subjectChartData = weeklyData?.subject_minutes ? 
    Object.entries(weeklyData.subject_minutes).map(([subject, minutes]) => ({
      subject,
      hours: Math.round(minutes / 60 * 10) / 10,
    })).sort((a, b) => b.hours - a.hours)
    : [];

  const monthlyHeatmap = monthlyData?.heatmap ? 
    Object.entries(monthlyData.heatmap).map(([date, minutes]) => ({
      date,
      minutes,
      hours: Math.round(minutes / 60 * 10) / 10,
    }))
    : [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
        <p className="text-slate-500">Track your progress and performance</p>
      </div>

      {/* Streak Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Current Streak</p>
              <p className="text-4xl font-bold mt-1">{streakData?.current_streak || 0}</p>
              <p className="text-orange-100 text-sm mt-1">days</p>
            </div>
            <Flame className="w-12 h-12 text-orange-200" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">Longest Streak</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{streakData?.longest_streak || 0}</p>
              <p className="text-slate-500 text-sm mt-1">days</p>
            </div>
            <Award className="w-10 h-10 text-amber-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">Total XP Earned</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{semesterData?.total_xp || 0}</p>
              <p className="text-slate-500 text-sm mt-1">points</p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-500" />
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="flex border-b border-slate-200">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 py-4 px-4 transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-50 text-primary-700 border-b-2 border-primary-500'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="p-6">
          {/* Daily Tab */}
          {activeTab === 'daily' && dailyData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Study Time</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {Math.floor((dailyData.metrics?.total_study_minutes || 0) / 60)}h {(dailyData.metrics?.total_study_minutes || 0) % 60}m
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Tasks Completed</p>
                  <p className="text-2xl font-bold text-slate-900">{dailyData.metrics?.tasks_completed || 0}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Tasks Missed</p>
                  <p className="text-2xl font-bold text-slate-900">{dailyData.metrics?.tasks_missed || 0}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">XP Earned</p>
                  <p className="text-2xl font-bold text-slate-900">{dailyData.metrics?.xp_earned || 0}</p>
                </div>
              </div>

              {dailyData.schedule && (
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Study Blocks Progress</h3>
                  <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all"
                      style={{ width: `${dailyData.schedule.completion_percentage}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-slate-500 mt-2">
                    {Math.round(dailyData.schedule.completion_percentage)}% Complete
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Weekly Tab */}
          {activeTab === 'weekly' && weeklyData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Total Hours</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {Math.round(weeklyData.total_study_minutes / 60 * 10) / 10}h
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Daily Average</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {Math.round(weeklyData.average_daily_minutes / 60 * 10) / 10}h
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Tasks Done</p>
                  <p className="text-2xl font-bold text-slate-900">{weeklyData.tasks_completed}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Week XP</p>
                  <p className="text-2xl font-bold text-slate-900">{weeklyData.total_xp}</p>
                </div>
              </div>

              {/* Weekly Bar Chart */}
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Daily Study Hours</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weeklyChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="date" stroke="#64748b" />
                      <YAxis stroke="#64748b" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#fff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="minutes" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Subject Distribution */}
              {subjectChartData.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Subject Distribution</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={subjectChartData}
                          dataKey="hours"
                          nameKey="subject"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          label={({ subject, hours }) => `${subject}: ${hours}h`}
                        >
                          {subjectChartData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Monthly Tab */}
          {activeTab === 'monthly' && monthlyData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Total Hours</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {Math.round(monthlyData.total_study_minutes / 60 * 10) / 10}h
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Daily Average</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {Math.round(monthlyData.average_daily_minutes / 60 * 10) / 10}h
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Tasks Done</p>
                  <p className="text-2xl font-bold text-slate-900">{monthlyData.tasks_completed}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Month XP</p>
                  <p className="text-2xl font-bold text-slate-900">{monthlyData.total_xp}</p>
                </div>
              </div>

              {/* Heatmap */}
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Study Heatmap</h3>
                <div className="grid grid-cols-7 gap-2">
                  {Array.from({ length: 31 }, (_, i) => i + 1).map(day => {
                    const dayData = monthlyHeatmap.find(d => {
                      const dayNum = parseInt(d.date.split('-')[2]);
                      return dayNum === day;
                    });
                    const intensity = dayData ? Math.min(dayData.minutes / 300, 1) : 0; // Max 5 hours = full intensity
                    
                    return (
                      <div
                        key={day}
                        className="aspect-square rounded flex items-center justify-center text-xs"
                        style={{
                          backgroundColor: `rgba(139, 92, 246, ${intensity})`,
                          color: intensity > 0.5 ? '#fff' : '#64748b',
                        }}
                        title={dayData ? `${dayData.hours} hours` : 'No data'}
                      >
                        {day}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Semester Tab */}
          {activeTab === 'semester' && semesterData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Total Hours</p>
                  <p className="text-2xl font-bold text-slate-900">{semesterData.total_study_hours}h</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Daily Average</p>
                  <p className="text-2xl font-bold text-slate-900">{semesterData.average_daily_hours}h</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Completion Rate</p>
                  <p className="text-2xl font-bold text-slate-900">{semesterData.completion_rate}%</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-sm text-slate-500">Total XP</p>
                  <p className="text-2xl font-bold text-slate-900">{semesterData.total_xp}</p>
                </div>
              </div>

              {/* Subject Progress */}
              {semesterData.subject_progress && semesterData.subject_progress.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Subject Progress</h3>
                  <div className="space-y-4">
                    {semesterData.subject_progress.map(subject => {
                      const completion = subject.total_topics > 0 
                        ? (subject.completed_topics?.length || 0) / subject.total_topics * 100 
                        : 0;
                      
                      return (
                        <div key={subject.subject_name} className="bg-slate-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-slate-900">{subject.subject_name}</span>
                            <span className="text-sm text-slate-500">
                              {subject.completed_topics?.length || 0}/{subject.total_topics} topics
                            </span>
                          </div>
                          <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all"
                              style={{ width: `${completion}%` }}
                            ></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Semester Summary */}
              <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-6 text-white">
                <h3 className="text-lg font-semibold mb-4">Semester Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-purple-200 text-sm">Days Covered</p>
                    <p className="text-2xl font-bold">{semesterData.days_covered}</p>
                  </div>
                  <div>
                    <p className="text-purple-200 text-sm">Tasks Completed</p>
                    <p className="text-2xl font-bold">{semesterData.tasks_completed}</p>
                  </div>
                  <div>
                    <p className="text-purple-200 text-sm">Tasks Missed</p>
                    <p className="text-2xl font-bold">{semesterData.tasks_missed}</p>
                  </div>
                  <div>
                    <p className="text-purple-200 text-sm">Success Rate</p>
                    <p className="text-2xl font-bold">{semesterData.completion_rate}%</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AMCAT Readiness Score */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">AMCAT Readiness Score</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['Quantitative', 'Logical', 'English', 'Coding', 'Core CS'].map((section, i) => (
            <div key={section} className="text-center">
              <div className="relative w-20 h-20 mx-auto">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle
                    cx="40"
                    cy="40"
                    r="35"
                    stroke="#e2e8f0"
                    strokeWidth="6"
                    fill="none"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="35"
                    stroke={COLORS[i]}
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${70 + i * 5} 220`}
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-lg font-bold text-slate-900">
                  {70 + i * 5}%
                </span>
              </div>
              <p className="text-sm text-slate-600 mt-2">{section}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;