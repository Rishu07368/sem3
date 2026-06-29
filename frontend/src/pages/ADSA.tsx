import { useState } from 'react';
import { BookOpen, Check, Circle, TrendingUp, Target, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const ADSA_TOPICS = [
  'Arrays', 'Strings', 'Recursion', 'Searching', 'Sorting',
  'Linked Lists', 'Stacks', 'Queues', 'Trees', 'Binary Search Trees',
  'AVL Trees', 'Heaps', 'Hashing', 'Graphs - BFS', 'Graphs - DFS',
  'Graphs - Shortest Paths', 'Greedy Algorithms', 'Backtracking', 'Dynamic Programming',
  'Dynamic Programming Advanced'
];

// Mock completed topics
const initialCompleted = ['Arrays', 'Strings', 'Recursion', 'Searching', 'Sorting', 'Linked Lists', 'Stacks', 'Queues', 'Trees'];

export default function ADSAPage() {
  const [completedTopics, setCompletedTopics] = useState<string[]>(initialCompleted);

  const toggleTopic = (topic: string) => {
    setCompletedTopics(prev => 
      prev.includes(topic) 
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const completedCount = completedTopics.length;
  const totalTopics = ADSA_TOPICS.length;
  const progress = (completedCount / totalTopics) * 100;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-primary-600">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Advanced Data Structures and Algorithms</h1>
              <p className="text-gray-400">Highest Placement Priority</p>
            </div>
          </div>
        </div>
        <Link to="/" className="btn btn-secondary">
          ← Back to Dashboard
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Target} label="Progress" value={`${progress.toFixed(0)}%`} color="primary" />
        <StatCard icon={Check} label="Completed" value={`${completedCount}/${totalTopics}`} color="green" />
        <StatCard icon={TrendingUp} label="Difficulty" value="9.5/10" color="red" />
        <StatCard icon={Zap} label="Priority" value="10/10" color="yellow" />
      </div>

      {/* Progress Bar */}
      <div className="card p-6">
        <div className="flex justify-between mb-2">
          <span className="text-gray-300">Overall Progress</span>
          <span className="text-white font-semibold">{progress.toFixed(1)}%</span>
        </div>
        <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Topics Grid */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary-400" />
          Topics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {ADSA_TOPICS.map((topic) => {
            const isCompleted = completedTopics.includes(topic);
            return (
              <div
                key={topic}
                className={`p-4 rounded-lg border transition-all ${
                  isCompleted
                    ? 'bg-green-900/30 border-green-700'
                    : 'bg-gray-700/50 border-gray-600 hover:border-primary-500'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    {isCompleted ? (
                      <div className="p-1 rounded-full bg-green-500 mt-0.5">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    ) : (
                      <Circle className="w-5 h-5 text-gray-500 mt-0.5" />
                    )}
                    <div>
                      <p className={`font-medium ${isCompleted ? 'text-green-300' : 'text-white'}`}>
                        {topic}
                      </p>
                    </div>
                  </div>
                  {!isCompleted && (
                    <button
                      onClick={() => toggleTopic(topic)}
                      className="btn btn-primary text-sm py-1 px-3"
                    >
                      Mark Done
                    </button>
                  )}
                  {isCompleted && (
                    <button
                      onClick={() => toggleTopic(topic)}
                      className="btn btn-secondary text-sm py-1 px-3"
                    >
                      Undo
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Weak Topics */}
      {false && (
        <div className="card p-6 border-orange-600">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-orange-400" />
            Topics Needing Revision
          </h2>
          <div className="flex flex-wrap gap-2">
            {subject.weak_topics.map((topic: string) => (
              <span
                key={topic}
                className="px-3 py-1 bg-orange-900/50 border border-orange-700 rounded-full text-orange-300 text-sm"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    primary: 'bg-primary-500/20 text-primary-400',
    green: 'bg-green-500/20 text-green-400',
    red: 'bg-red-500/20 text-red-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    orange: 'bg-orange-500/20 text-orange-400',
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
