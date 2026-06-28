import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format, addDays, subDays, isToday, isFuture, parseISO } from 'date-fns';
import {
  ChevronLeft, ChevronRight, Play, Pause, Square, CheckCircle,
  Clock, Target, TrendingUp, BookOpen, Dumbbell, Coffee, Home,
  Bus, Utensils, Moon, Sun, Brain, Zap, Calendar
} from 'lucide-react';
import { API_BASE } from '../App';

const ACTIVITY_ICONS = {
  'Sleep': Moon,
  'Breakfast': Coffee,
  'Travel to College': Bus,
  'College': Home,
  'Travel Back': Bus,
  'Gym': Dumbbell,
  'Dinner': Utensils,
  'Study': Brain,
  'AMCAT': Zap,
  'default': BookOpen,
};

const ACTIVITY_COLORS = {
  'Sleep': 'bg-slate-400',
  'Breakfast': 'bg-amber-400',
  'Travel to College': 'bg-blue-400',
  'College': 'bg-indigo-500',
  'Travel Back': 'bg-blue-400',
  'Gym': 'bg-green-500',
  'Dinner': 'bg-orange-400',
  'Study': 'bg-purple-500',
  'AMCAT': 'bg-rose-500',
  'default': 'bg-gray-500',
};

function DailyPage() {
  const { date } = useParams();
  const navigate = useNavigate();
  
  const [schedule, setSchedule] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activePomodoro, setActivePomodoro] = useState(null);
  const [pomodoroTime, setPomodoroTime] = useState(25 * 60);
  const [isPomodoroRunning, setIsPomodoroRunning] = useState(false);
  const [selectedDate, setSelectedDate] = useState(
    date ? parseISO(date) : new Date()
  );

  const fetchSchedule = useCallback(async (dateStr) => {
    try {
      const res = await fetch(`${API_BASE}/schedule/${dateStr}`);
      const data = await res.json();
      setSchedule(data);
      
      // Fetch metrics
      const metricsRes = await fetch(`${API_BASE}/metrics/${dateStr}`);
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);
    } catch (err) {
      console.error('Failed to fetch schedule:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    setIsLoading(true);
    const dateStr = format(selectedDate, 'yyyy-MM-dd');
    fetchSchedule(dateStr);
  }, [selectedDate, fetchSchedule]);

  const handlePreviousDay = () => {
    const newDate = subDays(selectedDate, 1);
    setSelectedDate(newDate);
    navigate(`/day/${format(newDate, 'yyyy-MM-dd')}`);
  };

  const handleNextDay = () => {
    const newDate = addDays(selectedDate, 1);
    setSelectedDate(newDate);
    navigate(`/day/${format(newDate, 'yyyy-MM-dd')}`);
  };

  const handleToday = () => {
    setSelectedDate(new Date());
    navigate('/');
  };

  const handleCompleteBlock = async (blockId) => {
    try {
      await fetch(`${API_BASE}/blocks/${blockId}/complete`, { method: 'POST' });
      fetchSchedule(format(selectedDate, 'yyyy-MM-dd'));
    } catch (err) {
      console.error('Failed to complete block:', err);
    }
  };

  const handleMissBlock = async (blockId) => {
    try {
      await fetch(`${API_BASE}/blocks/${blockId}/miss`, { method: 'POST' });
      fetchSchedule(format(selectedDate, 'yyyy-MM-dd'));
    } catch (err) {
      console.error('Failed to mark block as missed:', err);
    }
  };

  const handleStartPomodoro = async (blockId) => {
    try {
      const res = await fetch(`${API_BASE}/pomodoro/start/${blockId}`, { method: 'POST' });
      const data = await res.json();
      setActivePomodoro(data.session);
      setPomodoroTime(25 * 60);
      setIsPomodoroRunning(true);
    } catch (err) {
      console.error('Failed to start pomodoro:', err);
    }
  };

  const handlePausePomodoro = async () => {
    if (!activePomodoro) return;
    try {
      await fetch(`${API_BASE}/pomodoro/pause/${activePomodoro.id}`, { method: 'POST' });
      setIsPomodoroRunning(false);
    } catch (err) {
      console.error('Failed to pause pomodoro:', err);
    }
  };

  const handleFinishPomodoro = async () => {
    if (!activePomodoro) return;
    try {
      await fetch(`${API_BASE}/pomodoro/finish/${activePomodoro.id}`, { method: 'POST' });
      setActivePomodoro(null);
      setIsPomodoroRunning(false);
      setPomodoroTime(25 * 60);
      fetchSchedule(format(selectedDate, 'yyyy-MM-dd'));
    } catch (err) {
      console.error('Failed to finish pomodoro:', err);
    }
  };

  // Pomodoro timer effect
  useEffect(() => {
    let interval;
    if (isPomodoroRunning && pomodoroTime > 0) {
      interval = setInterval(() => {
        setPomodoroTime(prev => prev - 1);
      }, 1000);
    } else if (pomodoroTime === 0) {
      setIsPomodoroRunning(false);
      handleFinishPomodoro();
    }
    return () => clearInterval(interval);
  }, [isPomodoroRunning, pomodoroTime]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getActivityIcon = (activity) => {
    const Icon = ACTIVITY_ICONS[activity] || ACTIVITY_ICONS.default;
    return Icon;
  };

  const getActivityColor = (activity) => {
    return ACTIVITY_COLORS[activity] || ACTIVITY_COLORS.default;
  };

  const getModeBadge = (mode) => {
    const badges = {
      normal: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Normal Mode' },
      amcat: { bg: 'bg-rose-100', text: 'text-rose-700', label: 'AMCAT Mode' },
      exam: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Exam Mode' },
    };
    return badges[mode] || badges.normal;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const modeBadge = getModeBadge(schedule?.mode || 'normal');
  const isFutureDate = isFuture(selectedDate);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Date Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={handlePreviousDay}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </button>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3">
              <h2 className="text-2xl font-bold text-slate-900">
                {format(selectedDate, 'EEEE')}
              </h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${modeBadge.bg} ${modeBadge.text}`}>
                {modeBadge.label}
              </span>
            </div>
            <p className="text-slate-500 mt-1">
              {format(selectedDate, 'MMMM d, yyyy')}
              {isToday(selectedDate) && (
                <button
                  onClick={handleToday}
                  className="ml-2 text-primary-600 hover:text-primary-700 text-sm"
                >
                  (Today)
                </button>
              )}
            </p>
          </div>
          
          <button
            onClick={handleNextDay}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Daily Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Study Time</p>
              <p className="text-xl font-bold text-slate-900">
                {Math.floor((schedule?.total_study_minutes || 0) / 60)}h {((schedule?.total_study_minutes || 0) % 60)}m
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Completion</p>
              <p className="text-xl font-bold text-slate-900">
                {Math.round(schedule?.completion_percentage || 0)}%
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">XP Earned</p>
              <p className="text-xl font-bold text-slate-900">
                {metrics?.xp_earned || 0}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Tasks Done</p>
              <p className="text-xl font-bold text-slate-900">
                {metrics?.tasks_completed || 0}/{schedule?.study_blocks?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-700">Daily Progress</span>
          <span className="text-sm text-slate-500">
            {Math.round(schedule?.completion_percentage || 0)}%
          </span>
        </div>
        <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-primary-600 progress-bar rounded-full"
            style={{ width: `${schedule?.completion_percentage || 0}%` }}
          ></div>
        </div>
      </div>

      {/* Pomodoro Timer */}
      {activePomodoro && (
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-1">Focus Session Active</h3>
              <p className="text-purple-100 text-sm">
                {activePomodoro?.study_block?.subject || 'Study Block'}
              </p>
            </div>
            <div className="text-5xl font-mono font-bold">
              {formatTime(pomodoroTime)}
            </div>
            <div className="flex items-center space-x-2">
              {isPomodoroRunning ? (
                <button
                  onClick={handlePausePomodoro}
                  className="p-3 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                >
                  <Pause className="w-6 h-6" />
                </button>
              ) : (
                <button
                  onClick={() => setIsPomodoroRunning(true)}
                  className="p-3 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                >
                  <Play className="w-6 h-6" />
                </button>
              )}
              <button
                onClick={handleFinishPomodoro}
                className="p-3 bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                <Square className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Daily Timeline</h3>
        </div>
        
        <div className="divide-y divide-slate-100">
          {/* Fixed Time Slots */}
          {schedule?.fixed_slots?.map((slot) => {
            const Icon = getActivityIcon(slot.activity);
            const colorClass = getActivityColor(slot.activity);
            
            return (
              <div key={`fixed-${slot.id}`} className="p-4 flex items-center space-x-4 bg-slate-50/50">
                <div className="w-16 text-sm font-medium text-slate-500">
                  {slot.start_time} - {slot.end_time}
                </div>
                <div className={`w-10 h-10 ${colorClass} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-slate-700">{slot.activity}</p>
                  {slot.flexible_end && (
                    <p className="text-xs text-slate-400">Can extend to {slot.flexible_end}</p>
                  )}
                </div>
                <div className="text-xs px-2 py-1 bg-slate-200 text-slate-600 rounded">
                  Fixed
                </div>
              </div>
            );
          })}
          
          {/* Study Blocks */}
          {schedule?.study_blocks?.map((block) => {
            const isCompleted = block.completed;
            const isActive = activePomodoro?.id === block.id;
            
            return (
              <div
                key={block.id}
                className={`p-4 flex items-center space-x-4 transition-colors ${
                  isCompleted ? 'bg-green-50/50' : isActive ? 'bg-purple-50/50' : ''
                }`}
              >
                <div className="w-16 text-sm font-medium text-slate-500">
                  {block.start_time} - {block.end_time}
                </div>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  block.is_amcat ? 'bg-rose-500' :
                  block.is_revision ? 'bg-amber-500' : 'bg-purple-500'
                }`}>
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <p className="font-medium text-slate-900">{block.subject}</p>
                    {block.is_amcat && (
                      <span className="text-xs px-2 py-0.5 bg-rose-100 text-rose-700 rounded">AMCAT</span>
                    )}
                    {block.is_revision && (
                      <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded">Revision</span>
                    )}
                  </div>
                  <p className="text-sm text-slate-500">{block.topic}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {block.duration_minutes} minutes
                    {block.xp_earned > 0 && (
                      <span className="ml-2 text-amber-600">+{block.xp_earned} XP</span>
                    )}
                  </p>
                </div>
                
                {!isFutureDate && (
                  <div className="flex items-center space-x-2">
                    {!isCompleted && (
                      <>
                        {!isActive && (
                          <button
                            onClick={() => handleStartPomodoro(block.id)}
                            className="p-2 bg-primary-100 hover:bg-primary-200 text-primary-600 rounded-lg transition-colors"
                            title="Start Pomodoro"
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleCompleteBlock(block.id)}
                          className="p-2 bg-green-100 hover:bg-green-200 text-green-600 rounded-lg transition-colors"
                          title="Mark Complete"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleMissBlock(block.id)}
                          className="p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg transition-colors"
                          title="Mark as Missed"
                        >
                          <Square className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    {isCompleted && (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Mood & Energy Tracker */}
      {!isFutureDate && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">How are you feeling?</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Mood</label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <button
                    key={`mood-${level}`}
                    className={`w-10 h-10 rounded-lg transition-colors ${
                      metrics?.mood_rating === level
                        ? 'bg-yellow-400 text-white'
                        : 'bg-slate-100 text-slate-400 hover:bg-slate-200'
                    }`}
                    onClick={async () => {
                      await fetch(`${API_BASE}/metrics/${format(selectedDate, 'yyyy-MM-dd')}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mood_rating: level }),
                      });
                      fetchSchedule(format(selectedDate, 'yyyy-MM-dd'));
                    }}
                  >
                    {level === 1 && '😫'}
                    {level === 2 && '😕'}
                    {level === 3 && '😐'}
                    {level === 4 && '🙂'}
                    {level === 5 && '😊'}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Energy</label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <button
                    key={`energy-${level}`}
                    className={`w-10 h-10 rounded-lg transition-colors ${
                      metrics?.energy_rating === level
                        ? 'bg-orange-400 text-white'
                        : 'bg-slate-100 text-slate-400 hover:bg-slate-200'
                    }`}
                    onClick={async () => {
                      await fetch(`${API_BASE}/metrics/${format(selectedDate, 'yyyy-MM-dd')}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ energy_rating: level }),
                      });
                      fetchSchedule(format(selectedDate, 'yyyy-MM-dd'));
                    }}
                  >
                    {level === 1 && '🔋'}
                    {level === 2 && '🪫'}
                    {level === 3 && '⚡'}
                    {level === 4 && '💪'}
                    {level === 5 && '🚀'}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Notes */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">Notes</label>
            <textarea
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              rows="3"
              placeholder="Add notes about your study session..."
              defaultValue={metrics?.notes || ''}
              onBlur={async (e) => {
                await fetch(`${API_BASE}/metrics/${format(selectedDate, 'yyyy-MM-dd')}`, {
                  method: 'PUT',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ notes: e.target.value }),
                });
              }}
            ></textarea>
          </div>
        </div>
      )}
    </div>
  );
}

export default DailyPage;