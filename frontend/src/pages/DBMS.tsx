import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Database, Check, Circle, TrendingUp, Target, Zap, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

const DBMS_TOPICS = [
  'SQL Queries', 'Joins', 'Normalization', 'Transactions',
  'Indexes', 'ER Diagrams', 'Constraints', 'Practice Query Solving'
];

export default function DBMSPage() {
  const queryClient = useQueryClient();

  const { data: subject, isLoading } = useQuery({
    queryKey: ['subject', 'DBMS'],
    queryFn: () => api.getSubject('DBMS'),
  });

  const completeMutation = useMutation({
    mutationFn: ({ topic, confidence }: { topic: string; confidence: number }) =>
      api.completeTopic('DBMS', topic, confidence),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subject', 'DBMS'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const completedTopics = subject?.completed_topics || [];
  const completedCount = completedTopics.length;
  const totalTopics = DBMS_TOPICS.length;
  const progress = (completedCount / totalTopics) * 100;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-blue-600">
            <Database className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Database Management System</h1>
            <p className="text-gray-400">High Placement Importance</p>
          </div>
        </div>
        <Link to="/" className="btn btn-secondary">← Back to Dashboard</Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Target} label="Progress" value={`${progress.toFixed(0)}%`} color="blue" />
        <StatCard icon={Check} label="Completed" value={`${completedCount}/${totalTopics}`} color="green" />
        <StatCard icon={TrendingUp} label="Difficulty" value="7.5/10" color="yellow" />
        <StatCard icon={Zap} label="Importance" value="9/10" color="purple" />
      </div>

      <div className="card p-6">
        <div className="flex justify-between mb-2">
          <span className="text-gray-300">Overall Progress</span>
          <span className="text-white font-semibold">{progress.toFixed(1)}%</span>
        </div>
        <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-400" />
          Topics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {DBMS_TOPICS.map((topic) => {
            const isCompleted = completedTopics.includes(topic);
            return (
              <div
                key={topic}
                className={`p-4 rounded-lg border ${
                  isCompleted ? 'bg-green-900/30 border-green-700' : 'bg-gray-700/50 border-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {isCompleted ? (
                      <div className="p-1 rounded-full bg-green-500"><Check className="w-4 h-4 text-white" /></div>
                    ) : (
                      <Circle className="w-5 h-5 text-gray-500" />
                    )}
                    <span className={`font-medium ${isCompleted ? 'text-green-300' : 'text-white'}`}>{topic}</span>
                  </div>
                  {!isCompleted && (
                    <button
                      onClick={() => completeMutation.mutate({ topic, confidence: 0.7 })}
                      className="btn btn-primary text-sm py-1 px-3"
                      disabled={completeMutation.isPending}
                    >
                      Done
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-500/20 text-blue-400',
    green: 'bg-green-500/20 text-green-400',
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
