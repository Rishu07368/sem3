import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { api } from '@/services/api';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const navigate = useNavigate();

  const { data: schedules } = useQuery({
    queryKey: ['schedules', format(currentDate, 'yyyy-MM')],
    queryFn: () => api.getSchedules(
      format(startOfMonth(currentDate), 'yyyy-MM-dd'),
      format(endOfMonth(currentDate), 'yyyy-MM-dd')
    ),
  });

  const { data: heatmapData } = useQuery({
    queryKey: ['heatmap', currentDate.getFullYear(), currentDate.getMonth() + 1],
    queryFn: () => api.getHeatmap(currentDate.getFullYear(), currentDate.getMonth() + 1),
  });

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const heatmapMap = new Map(
    heatmapData?.heatmap?.map((h: { date: string; intensity: number }) => [h.date, h.intensity]) || []
  );

  const scheduleMap = new Map(
    schedules?.schedules?.map((s: { date: string; completion_percentage: number }) => [s.date, s]) || []
  );

  const getDayColor = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const intensity = heatmapMap.get(dateStr);
    
    if (isToday(date)) return 'bg-blue-500 ring-2 ring-blue-400';
    if (!isSameMonth(date, currentDate)) return 'bg-gray-800/50 text-gray-600';
    
    switch (intensity) {
      case 4: return 'bg-green-400';
      case 3: return 'bg-green-500';
      case 2: return 'bg-green-600';
      case 1: return 'bg-green-800';
      default: return 'bg-gray-700 hover:bg-gray-600';
    }
  };

  const handleDayClick = (date: Date) => {
    navigate(`/schedule/${format(date, 'yyyy-MM-dd')}`);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <CalendarIcon className="w-7 h-7 text-primary-400" />
            Calendar
          </h1>
          <p className="text-gray-400 mt-1">Track your study progress and view schedules</p>
        </div>
      </div>

      {/* Calendar */}
      <div className="card p-6">
        {/* Month Navigation */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => setCurrentDate(subMonths(currentDate, 1))}
            className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-400" />
          </button>
          <h2 className="text-xl font-semibold text-white">
            {format(currentDate, 'MMMM yyyy')}
          </h2>
          <button
            onClick={() => setCurrentDate(addMonths(currentDate, 1))}
            className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Day Headers */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="text-center text-sm font-medium text-gray-400 py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {days.map((day) => {
            const dateStr = format(day, 'yyyy-MM-dd');
            const schedule = scheduleMap.get(dateStr);
            
            return (
              <button
                key={dateStr}
                onClick={() => handleDayClick(day)}
                className={`aspect-square rounded-lg flex flex-col items-center justify-center ${getDayColor(day)} transition-all hover:scale-105 cursor-pointer`}
              >
                <span className="text-sm font-medium">{format(day, 'd')}</span>
                {schedule && (
                  <div className="w-1.5 h-1.5 rounded-full bg-white/50 mt-0.5" />
                )}
              </button>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-6 flex items-center justify-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-700" />
            <span className="text-sm text-gray-400">No study</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-800" />
            <span className="text-sm text-gray-400">Light</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500" />
            <span className="text-sm text-gray-400">Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-400" />
            <span className="text-sm text-gray-400">Intense</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-500 ring-2 ring-blue-400" />
            <span className="text-sm text-gray-400">Today</span>
          </div>
        </div>
      </div>

      {/* Heatmap Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <p className="text-sm text-gray-400">Active Days</p>
          <p className="text-2xl font-bold text-green-400">
            {heatmapData?.heatmap?.filter((h: { intensity: number }) => h.intensity > 0).length || 0}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Total Hours</p>
          <p className="text-2xl font-bold text-blue-400">
            {((heatmapData?.heatmap?.reduce((acc: number, h: { minutes: number }) => acc + h.minutes, 0) || 0) / 60).toFixed(1)}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Best Day</p>
          <p className="text-2xl font-bold text-yellow-400">
            {heatmapData?.heatmap?.reduce((best: { minutes: number }, h: { minutes: number }) => 
              h.minutes > best.minutes ? h : best, { minutes: 0 })?.date?.split('-')[2] || '-'}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Consistency</p>
          <p className="text-2xl font-bold text-purple-400">
            {((heatmapData?.heatmap?.filter((h: { intensity: number }) => h.intensity > 0).length / days.length) * 100).toFixed(0)}%
          </p>
        </div>
      </div>
    </div>
  );
}
