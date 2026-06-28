import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import {
  Settings as SettingsIcon, Clock, Calendar, RefreshCw, Save,
  AlertCircle, CheckCircle, Loader2, BookOpen, Target, Zap
} from 'lucide-react';
import { API_BASE } from '../App';

function SettingsPage() {
  const [config, setConfig] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API_BASE}/config`);
      const data = await res.json();
      setConfig(data.config || {});
    } catch (err) {
      console.error('Failed to fetch config:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setMessage(null);

      for (const [key, value] of Object.entries(config)) {
        await fetch(`${API_BASE}/config/${key}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ value }),
        });
      }

      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleRegenerate = async () => {
    try {
      setIsGenerating(true);
      setMessage(null);

      const res = await fetch(`${API_BASE}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: config.start_date,
          end_date: config.end_date,
          amcat_start_date: config.amcat_start_date,
          amcat_end_date: config.amcat_end_date,
          exam_start_date: config.exam_start_date,
        }),
      });

      const data = await res.json();
      setMessage({ type: 'success', text: data.message || 'Timetable regenerated successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to regenerate timetable' });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setMessage(null);

      const res = await fetch(`${API_BASE}/generate`, { method: 'POST' });
      const data = await res.json();
      setMessage({ type: 'success', text: data.message || 'Timetable generated successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to generate timetable' });
    } finally {
      setIsGenerating(false);
    }
  };

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
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500">Configure your timetable engine and constraints</p>
      </div>

      {/* Message */}
      {message && (
        <div className={`flex items-center space-x-3 p-4 rounded-xl ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-600" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Date Range Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Calendar className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Date Range</h2>
            <p className="text-sm text-slate-500">Set the start and end dates for your semester</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Start Date</label>
            <input
              type="date"
              value={config.start_date || ''}
              onChange={(e) => handleChange('start_date', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">End Date</label>
            <input
              type="date"
              value={config.end_date || ''}
              onChange={(e) => handleChange('end_date', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Schedule Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
            <Clock className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Schedule Constraints</h2>
            <p className="text-sm text-slate-500">Configure fixed daily activities</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Sleep Start</label>
            <input
              type="time"
              value={config.sleep_start || '23:30'}
              onChange={(e) => handleChange('sleep_start', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Wake Up</label>
            <input
              type="time"
              value={config.sleep_end || '07:00'}
              onChange={(e) => handleChange('sleep_end', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">College Start</label>
            <input
              type="time"
              value={config.college_start || '09:30'}
              onChange={(e) => handleChange('college_start', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">College End</label>
            <input
              type="time"
              value={config.college_end || '16:30'}
              onChange={(e) => handleChange('college_end', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Gym Start</label>
            <input
              type="time"
              value={config.gym_start || '17:30'}
              onChange={(e) => handleChange('gym_start', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Gym End</label>
            <input
              type="time"
              value={config.gym_end || '19:00'}
              onChange={(e) => handleChange('gym_end', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      {/* AMCAT Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-rose-100 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-rose-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">AMCAT Mode</h2>
            <p className="text-sm text-slate-500">Set the AMCAT preparation period</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">AMCAT Start Date</label>
            <input
              type="date"
              value={config.amcat_start_date || ''}
              onChange={(e) => handleChange('amcat_start_date', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">AMCAT End Date</label>
            <input
              type="date"
              value={config.amcat_end_date || ''}
              onChange={(e) => handleChange('amcat_end_date', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        <div className="mt-4 p-4 bg-rose-50 rounded-lg">
          <p className="text-sm text-rose-800">
            <strong>AMCAT Mode:</strong> During this period, the scheduler will automatically increase 
            time allocation for Quantitative Aptitude, Logical Reasoning, English, Coding, and 
            Debugging while reducing normal semester study time.
          </p>
        </div>
      </div>

      {/* Exam Mode Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <Target className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Exam Mode</h2>
            <p className="text-sm text-slate-500">Set the exam date (3 weeks before triggers revision mode)</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Exam Start Date</label>
            <input
              type="date"
              value={config.exam_start_date || ''}
              onChange={(e) => handleChange('exam_start_date', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Weeks Before Exam</label>
            <input
              type="number"
              min="1"
              max="6"
              value={config.exam_weeks_before || '3'}
              onChange={(e) => handleChange('exam_weeks_before', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-800">
            <strong>Exam Mode:</strong> During the final 3 weeks before exams, the scheduler will 
            automatically switch to revision mode, increasing time for Mock Papers, Previous Year 
            Questions, and Weak Topics while reducing new learning.
          </p>
        </div>
      </div>

      {/* Subject Priorities */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Subject Priorities</h2>
            <p className="text-sm text-slate-500">Current subject allocation (cannot be modified here)</p>
          </div>
        </div>

        <div className="space-y-3">
          {[
            { name: 'ADSA', hours: '12-15', priority: 1 },
            { name: 'COA', hours: '8-10', priority: 2 },
            { name: 'DBMS', hours: '8-10', priority: 3 },
            { name: 'Probability', hours: '6-8', priority: 4 },
            { name: 'Python', hours: '2-3', priority: 5 },
            { name: 'UHV', hours: '1', priority: 6 },
            { name: 'Soft Skills', hours: '1', priority: 7 },
          ].map(subject => (
            <div key={subject.name} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold">
                  {subject.priority}
                </span>
                <span className="font-medium text-slate-900">{subject.name}</span>
              </div>
              <span className="text-sm text-slate-500">{subject.hours} hrs/week</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end space-x-4">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center space-x-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {isSaving ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Save className="w-5 h-5" />
          )}
          <span>Save Settings</span>
        </button>
        
        <button
          onClick={handleRegenerate}
          disabled={isGenerating}
          className="flex items-center space-x-2 px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {isGenerating ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <RefreshCw className="w-5 h-5" />
          )}
          <span>Regenerate Timetable</span>
        </button>
      </div>

      {/* Important Note */}
      <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Important Notes</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• Changing constraints will automatically regenerate the entire timetable</li>
          <li>• The scheduling engine is reusable - changing college timing, gym duration, or exam dates will trigger a full regeneration</li>
          <li>• AMCAT mode automatically increases aptitude study time between specified dates</li>
          <li>• Exam mode activates 3 weeks before the exam date for focused revision</li>
          <li>• Subject priorities are based on placement importance and difficulty</li>
        </ul>
      </div>
    </div>
  );
}

export default SettingsPage;