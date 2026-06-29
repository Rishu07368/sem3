import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Cpu, Check, Circle, TrendingUp, Target, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const COA_TOPICS = [
  'Number Systems', 'Boolean Algebra', 'CPU Organization', 'Registers',
  'Instruction Cycle', 'Memory Hierarchy', 'Cache Memory', 'Pipelining',
  'Interrupts', 'Input/Output Organization'
];

export default function COAPage() {
  const queryClient = useQueryClient();

  const { data: subject } = useQuery({
    queryKey: ['subject', 'COA'],
    queryFn: () => api.getSubject('COA'),
  });

  const completeMutation = useMutation({
    mutationFn: ({ topic, confidence }: { topic: string; confidence: number }) =>
      api.completeTopic('COA', topic, confidence),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subject', 'COA'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const completedTopics = subject?.completed_topics || [];
  const completedCount = completedTopics.length;
  const totalTopics = COA_TOPICS.length;
  const progress = (completedCount / totalTopics) * 100;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-purple-600">
            <Cpu className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Computer Organization and Architecture</h1>
            <p className="text-gray-400">Core CS Subject</p>
          </div>
        </div>
        <Link to="/" className="btn btn-secondary">← Back to Dashboard</Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Target} label="Progress" value={`${progress.toFixed(0)}%`} color="purple" />
        <StatCard icon={Check} label="Completed" value={`${completedCount}/${totalTopics}`} color="green" />
        <StatCard icon={TrendingUp} label="Difficulty" value="8.5/10" color="red" />
        <StatCard icon={Zap} label="Importance" value="8/10" color="yellow" />
      </div>

      <div className="card p-6">
        <div className="flex justify-between mb-2">
          <span className="text-gray-300">Overall Progress</span>
          <span className="text-white font-semibold">{progress.toFixed(1)}%</span>
        </div>
        <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-purple-400" />
          Topics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {COA_TOPICS.map((topic) => {
            const isCompleted = completedTopics.includes(topic);
            return (
              <div key={topic} className={`p-4 rounded-lg border ${isCompleted ? 'bg-green-900/30 border-green-700' : 'bg-gray-700/50 border-gray-600'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {isCompleted ? <div className="p-1 rounded-full bg-green-500"><Check className="w-4 h-4 text-white" /></div> : <Circle className="w-5 h-5 text-gray-500" />}
                    <span className={`font-medium ${isCompleted ? 'text-green-300' : 'text-white'}`}>{topic}</span>
                  </div>
                  {!isCompleted && (
                    <button onClick={() => completeMutation.mutate({ topic, confidence: 0.7 })} className="btn btn-primary text-sm py-1 px-3" disabled={completeMutation.isPending}>Done</button>
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
  const colors: Record<string, string> = { purple: 'bg-purple-500/20 text-purple-400', green: 'bg-green-500/20 text-green-400', red: 'bg-red-500/20 text-red-400', yellow: 'bg-yellow-500/20 text-yellow-400' };
  return <div className="card p-4"><div className="flex items-center gap-3"><div className={`p-2 rounded-lg ${colors[color]}`}><Icon className="w-5 h-5" /></div><div><p className="text-sm text-gray-400">{label}</p><p className="text-xl font-bold text-white">{value}</p></div></div></div>;
}
