import { Briefcase, Target, Clock, TrendingUp, Calculator, Brain, Book, Code, Bug, Cpu, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

// Mock AMCAT data
const mockSections = [
  { name: 'Quantitative Aptitude', progress: 45, hours: 20, color: 'blue' },
  { name: 'Logical Reasoning', progress: 30, hours: 15, color: 'purple' },
  { name: 'English', progress: 60, hours: 10, color: 'green' },
  { name: 'Coding', progress: 25, hours: 15, color: 'red' },
  { name: 'Debugging', progress: 50, hours: 8, color: 'orange' },
  { name: 'Core CS', progress: 40, hours: 5, color: 'yellow' },
];

export default function AMCATPage() {

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600">
            <Briefcase className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">AMCAT Preparation</h1>
            <p className="text-gray-400">Aptitude & Skills Assessment</p>
          </div>
        </div>
        <Link to="/" className="btn btn-secondary">← Back to Dashboard</Link>
      </div>

      {/* Countdown & Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-6 bg-gradient-to-br from-purple-900/50 to-blue-900/50 border-purple-700">
          <div className="flex items-center gap-4">
            <Clock className="w-10 h-10 text-purple-400" />
            <div>
              <p className="text-sm text-gray-400">Days Until AMCAT</p>
              <p className="text-4xl font-bold text-white">{45}</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <p className="text-sm text-gray-400">Readiness Score</p>
          <p className="text-4xl font-bold text-green-400">{72}%</p>
          <p className="text-sm text-gray-400 mt-1">{'On Track'}</p>
        </div>
        <div className="card p-6">
          <p className="text-sm text-gray-400">Practice Completed</p>
          <p className="text-4xl font-bold text-blue-400">{15}/{50}</p>
          <p className="text-sm text-gray-400 mt-1">Blocks</p>
        </div>
      </div>

      {/* Sections */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-primary-400" />
          AMCAT Sections
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {AMCAT_SECTIONS.map((section) => {
            const Icon = section.icon;
            const progress = section.progress;
            return (
              <div key={section.name} className="p-4 rounded-lg bg-gray-700/50 border border-gray-600">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`p-2 rounded-lg bg-${section.color}-500/20`}>
                    <Icon className={`w-5 h-5 text-${section.color}-400`} />
                  </div>
                  <div>
                    <p className="font-medium text-white">{section.name}</p>
                    <p className="text-sm text-gray-400">{section.hours}h target</p>
                  </div>
                </div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Progress</span>
                  <span className="text-white">{progress.toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-gray-600 rounded-full overflow-hidden">
                  <div className={`h-full bg-${section.color}-500 rounded-full`} style={{ width: `${progress}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tips */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-green-400" />
          Preparation Tips
        </h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-gray-700/50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
            <p className="text-gray-300">Practice Quantitative Aptitude daily for at least 30 minutes</p>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-700/50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
            <p className="text-gray-300">Solve previous year AMCAT papers to understand pattern</p>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-700/50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
            <p className="text-gray-300">Focus on speed and accuracy - you have limited time per question</p>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-700/50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
            <p className="text-gray-300">Code in Python/C++ regularly - coding section is crucial</p>
          </div>
        </div>
      </div>
    </div>
  );
}
