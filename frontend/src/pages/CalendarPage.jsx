import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, getDay, addMonths, subMonths, isSameMonth, isSameDay, isToday } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, TrendingUp } from 'lucide-react';
import { API_BASE } from '../App';

const STATUS_COLORS = {
  completed: {
    bg: 'bg-green-500',
    text: 'text-white',
    border: 'border-green-600',
    hover: 'hover:bg-green-600',
  },
  partial: {
    bg: 'bg-yellow-400',
    text: 'text-yellow-900',
    border: 'border-yellow-500',
    hover: 'hover:bg-yellow-500',
  },
  pending: {
    bg: 'bg-slate-200',
    text: 'text-slate-600',
    border: 'border-slate-300',
    hover: 'hover:bg-slate-300',
  },
  missed: {
    bg: 'bg-red-400',
    text: 'text-white',
    border: 'border-red-500',
    hover: 'hover:bg-red-500',
  },
  current: {
    bg: 'bg-primary-500',
    text: 'text-white',
    border: 'border-primary-600',
    hover: 'hover:bg-primary-600',
  },
  future: {
    bg: 'bg-slate-100',
    text: 'text-slate-400',
    border: 'border-slate-200',
    hover: 'hover:bg-slate-200',
  },
};

function CalendarPage() {
  const navigate = useNavigate();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [calendarData, setCalendarData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(null);
  const [monthStats, setMonthStats] = useState(null);

  const fetchCalendarData = useCallback(async (year, month) => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE}/calendar?year=${year}&month=${month}`);
      const data = await res.json();
      
      const dataMap = {};
      data.days.forEach(day => {
        dataMap[day.date] = day;
      });
      
      setCalendarData(dataMap);
      setMonthStats(data);
    } catch (err) {
      console.error('Failed to fetch calendar data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCalendarData(currentMonth.getFullYear(), currentMonth.getMonth() + 1);
  }, [currentMonth, fetchCalendarData]);

  const handlePreviousMonth = () => {
    setCurrentMonth(prev => subMonths(prev, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(prev => addMonths(prev, 1));
  };

  const handleDayClick = (date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    navigate(`/day/${dateStr}`);
  };

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });
  
  // Get day of week for first day (0 = Sunday, adjust for Monday start)
  const startDayOfWeek = (getDay(monthStart) + 6) % 7; // Monday = 0
  
  // Pad the beginning with empty cells
  const paddedDays = [...Array(startDayOfWeek).fill(null), ...daysInMonth];

  const getStatusColor = (date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const data = calendarData[dateStr];
    
    if (isToday(date)) return STATUS_COLORS.current;
    if (!data) return STATUS_COLORS.pending;
    
    return STATUS_COLORS[data.status] || STATUS_COLORS.pending;
  };

  const getCompletionPercentage = (date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const data = calendarData[dateStr];
    return data?.completion_percentage || 0;
  };

  // Calculate month statistics
  const completedDays = Object.values(calendarData).filter(d => d?.status === 'completed').length;
  const partialDays = Object.values(calendarData).filter(d => d?.status === 'partial').length;
  const totalDays = daysInMonth.length;
  const monthProgress = totalDays > 0 ? Math.round(((completedDays + partialDays * 0.5) / totalDays) * 100) : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Calendar View</h1>
          <p className="text-slate-500">Click any day to view its detailed schedule</p>
        </div>
        
        {/* Month Navigation */}
        <div className="flex items-center space-x-4">
          <button
            onClick={handlePreviousMonth}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </button>
          <h2 className="text-xl font-semibold text-slate-900 min-w-[200px] text-center">
            {format(currentMonth, 'MMMM yyyy')}
          </h2>
          <button
            onClick={handleNextMonth}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Month Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Month Progress</p>
              <p className="text-xl font-bold text-slate-900">{monthProgress}%</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-white rounded-full"></div>
            </div>
            <div>
              <p className="text-sm text-slate-500">Completed</p>
              <p className="text-xl font-bold text-slate-900">{completedDays}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-400 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-yellow-900 rounded-full"></div>
            </div>
            <div>
              <p className="text-sm text-slate-500">Partial</p>
              <p className="text-xl font-bold text-slate-900">{partialDays}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-slate-200 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-slate-500 rounded-full"></div>
            </div>
            <div>
              <p className="text-sm text-slate-500">Remaining</p>
              <p className="text-xl font-bold text-slate-900">{totalDays - completedDays - partialDays}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Day Headers */}
        <div className="grid grid-cols-7 bg-slate-50 border-b border-slate-200">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
            <div
              key={day}
              className="py-3 text-center text-sm font-medium text-slate-600"
            >
              {day}
            </div>
          ))}
        </div>
        
        {/* Calendar Days */}
        <div className="grid grid-cols-7">
          {paddedDays.map((date, index) => {
            if (!date) {
              return (
                <div
                  key={`empty-${index}`}
                  className="min-h-[100px] bg-slate-50/30 border-b border-r border-slate-100"
                ></div>
              );
            }
            
            const statusColor = getStatusColor(date);
            const completion = getCompletionPercentage(date);
            const dateStr = format(date, 'yyyy-MM-dd');
            const data = calendarData[dateStr];
            
            return (
              <div
                key={dateStr}
                onClick={() => handleDayClick(date)}
                className={`min-h-[100px] p-2 border-b border-r border-slate-100 cursor-pointer transition-all calendar-day ${statusColor.bg} ${statusColor.hover}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-sm font-medium ${statusColor.text}`}>
                    {format(date, 'd')}
                  </span>
                  {isToday(date) && (
                    <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                  )}
                </div>
                
                {data && (
                  <div className="space-y-1">
                    {/* Mode indicator */}
                    {data.mode !== 'normal' && (
                      <span className={`inline-block text-[10px] px-1 py-0.5 rounded ${
                        data.mode === 'amcat' ? 'bg-rose-200 text-rose-800' : 'bg-amber-200 text-amber-800'
                      }`}>
                        {data.mode.toUpperCase()}
                      </span>
                    )}
                    
                    {/* Completion bar */}
                    {completion > 0 && (
                      <div className="h-1 bg-white/30 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-white rounded-full transition-all"
                          style={{ width: `${completion}%` }}
                        ></div>
                      </div>
                    )}
                    
                    {/* Study time */}
                    {data.total_study_minutes > 0 && (
                      <p className={`text-[10px] ${statusColor.text}`}>
                        {Math.floor(data.total_study_minutes / 60)}h {data.total_study_minutes % 60}m
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <h3 className="text-sm font-medium text-slate-700 mb-3">Legend</h3>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-primary-500 rounded"></div>
            <span className="text-sm text-slate-600">Today</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span className="text-sm text-slate-600">Completed</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-400 rounded"></div>
            <span className="text-sm text-slate-600">Partial</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-400 rounded"></div>
            <span className="text-sm text-slate-600">Missed</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-slate-200 rounded"></div>
            <span className="text-sm text-slate-600">Pending</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-slate-100 rounded"></div>
            <span className="text-sm text-slate-600">Future</span>
          </div>
        </div>
      </div>

      {/* AMCAT/Exam Mode Indicators */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <h3 className="text-sm font-medium text-slate-700 mb-3">Upcoming Mode Changes</h3>
        <div className="space-y-2">
          {Object.entries(calendarData)
            .filter(([dateStr, data]) => data.mode !== 'normal')
            .slice(0, 5)
            .map(([dateStr, data]) => (
              <div key={dateStr} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <div className="flex items-center space-x-3">
                  <CalendarIcon className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-700">{format(new Date(dateStr), 'EEEE, MMM d')}</span>
                </div>
                <span className={`text-sm font-medium px-2 py-1 rounded ${
                  data.mode === 'amcat' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                }`}>
                  {data.mode.toUpperCase()} Mode
                </span>
              </div>
            ))}
          {Object.entries(calendarData).filter(([_, data]) => data.mode !== 'normal').length === 0 && (
            <p className="text-sm text-slate-500">No special modes scheduled for this month</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default CalendarPage;