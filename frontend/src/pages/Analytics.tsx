import { BarChart3, TrendingUp, Clock, Trophy, Flame, Star, Calendar, BookOpen } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Link } from 'react-router-dom';

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

// Mock data
const subjectData = [
  { name: 'ADSA', completed: 12, total: 20, hours: 45 },
  { name: 'DBMS', completed: 5, total: 8, hours: 25 },
  { name: 'COA', completed: 4, total: 10, hours: 20 },
  { name: 'Probability', completed: 3, total: 8, hours: 15 },
  { name: 'Python', completed: 4, total: 6, hours: 8 },
];

const weeklyData = [
  { day: 'Mon', hours: 4.5 },
  { day: 'Tue', hours: 3.2 },
  { day: 'Wed', hours: 5.0 },
  { day: 'Thu', hours: 2.8 },
  { day: 'Fri', hours: 4.0 },
  { day: 'Sat', hours: 6.5 },
  { day: 'Sun', hours: 3.0 },
];

export default function AnalyticsPage() {

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <BarChart3 className="w-7 h-7 text-primary-400" />
            Analytics
          </h1>
          <p className="text-gray-400 mt-1">Track your progress and insights</p>
        </div>
        <Link to="/" className="btn btn-secondary">← Back to Dashboard</Link>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Clock} label="Total Hours" value={`${"113.0"}h`} color="blue" />
        <StatCard icon={Trophy} label="Tasks Done" value={`${85}`} color="green" />
        <StatCard icon={Flame} label="Current Streak" value={`${5} days`} color="orange" />
        <StatCard icon={Star} label="Total XP" value={`${1250}`} color="yellow" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Study */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            Weekly Study Hours
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="day" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="hours" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Subject Distribution */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-green-400" />
            Subject Progress
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={subjectData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="completed"
                  nameKey="name"
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {subjectData.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-400" />
          Subject Details
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-3">Subject</th>
                <th className="pb-3">Completed</th>
                <th className="pb-3">Total</th>
                <th className="pb-3">Progress</th>
                <th className="pb-3">Hours</th>
              </tr>
            </thead>
            <tbody>
              {subjectData.map((subject: any) => (
                <tr key={subject.name} className="border-b border-gray-700/50">
                  <td className="py-3 text-white">{subject.name}</td>
                  <td className="py-3 text-green-400">{subject.completed}</td>
                  <td className="py-3 text-gray-400">{subject.total}</td>
                  <td className="py-3 w-32">
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 rounded-full" style={{ width: `${(subject.completed / subject.total) * 100}%` }} />
                    </div>
                  </td>
                  <td className="py-3 text-gray-400">{subject.hours?.toFixed(1) || 0}h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-500/20 text-blue-400',
    green: 'bg-green-500/20 text-green-400',
    orange: 'bg-orange-500/20 text-orange-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    purple: 'bg-purple-500/20 text-purple-400',
  };
  return (
    <div className="card p-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}><Icon className="w-5 h-5" /></div>
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}
