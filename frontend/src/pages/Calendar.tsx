import { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';

// Mock heatmap data - intensity 0-4
const mockHeatmap = [
  { date: '2025-07-14', intensity: 2, minutes: 120 },
  { date: '2025-07-15', intensity: 3, minutes: 180 },
  { date: '2025-07-16', intensity: 1, minutes: 60 },
  { date: '2025-07-17', intensity: 4, minutes: 240 },
  { date: '2025-07-18', intensity: 2, minutes: 90 },
  { date: '2025-07-19', intensity: 0, minutes: 0 },
  { date: '2025-07-20', intensity: 3, minutes: 150 },
  { date: '2025-07-21', intensity: 4, minutes: 200 },
  { date: '2025-07-22', intensity: 2, minutes: 100 },
  { date: '2025-07-23', intensity: 3, minutes: 160 },
];

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const heatmapMap = new Map(
    mockHeatmap.map((h) => [h.date, h])
  );

  const getDayColor = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const dayData = heatmapMap.get(dateStr);
    const intensity = dayData?.intensity || 0;
    
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

  const activeDays = mockHeatmap.filter(h => h.intensity > 0).length;
  const totalMinutes = mockHeatmap.reduce((acc, h) => acc + h.minutes, 0);
  const consistency = Math.round((activeDays / 30) * 100);

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
            const hasStudy = heatmapMap.has(dateStr);
            
            return (
              <div
                key={dateStr}
                className={`aspect-square rounded-lg flex flex-col items-center justify-center ${getDayColor(day)} transition-all`}
              >
                <span className="text-sm font-medium">{format(day, 'd')}</span>
                {hasStudy && (
                  <div className="w-1.5 h-1.5 rounded-full bg-white/50 mt-0.5" />
                )}
              </div>
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
          <p className="text-2xl font-bold text-green-400">{activeDays}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Total Hours</p>
          <p className="text-2xl font-bold text-blue-400">{(totalMinutes / 60).toFixed(1)}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Best Day</p>
          <p className="text-2xl font-bold text-yellow-400">17</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Consistency</p>
          <p className="text-2xl font-bold text-purple-400">{consistency}%</p>
        </div>
      </div>
    </div>
  );
}
