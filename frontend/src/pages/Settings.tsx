import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Settings as SettingsIcon, User, Bell, Moon, LogOut, Save } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <SettingsIcon className="w-7 h-7 text-primary-400" />
          Settings
        </h1>
        <p className="text-gray-400 mt-1">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <User className="w-5 h-5 text-blue-400" />
          Profile
        </h2>
        <div className="space-y-4">
          <div>
            <label className="label">Username</label>
            <input type="text" value={user?.username || ''} disabled className="input bg-gray-600/50" />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" value={user?.email || ''} disabled className="input bg-gray-600/50" />
          </div>
          <div>
            <label className="label">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input"
              placeholder="Your full name"
            />
          </div>
          <button onClick={handleSave} className="btn btn-primary flex items-center gap-2">
            <Save className="w-4 h-4" />
            {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <User className="w-5 h-5 text-green-400" />
          Your Stats
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-700/50 rounded-lg">
            <p className="text-sm text-gray-400">Level</p>
            <p className="text-2xl font-bold text-yellow-400">{user?.level || 1}</p>
          </div>
          <div className="p-4 bg-gray-700/50 rounded-lg">
            <p className="text-sm text-gray-400">Total XP</p>
            <p className="text-2xl font-bold text-primary-400">{user?.xp || 0}</p>
          </div>
          <div className="p-4 bg-gray-700/50 rounded-lg">
            <p className="text-sm text-gray-400">Current Streak</p>
            <p className="text-2xl font-bold text-orange-400">{user?.current_streak || 0}</p>
          </div>
          <div className="p-4 bg-gray-700/50 rounded-lg">
            <p className="text-sm text-gray-400">Longest Streak</p>
            <p className="text-2xl font-bold text-green-400">{user?.longest_streak || 0}</p>
          </div>
        </div>
      </div>

      {/* Logout */}
      <div className="card p-6">
        <button onClick={logout} className="btn btn-danger w-full flex items-center justify-center gap-2">
          <LogOut className="w-4 h-4" />
          Log Out
        </button>
      </div>

      {/* Links */}
      <div className="text-center">
        <Link to="/" className="text-gray-400 hover:text-white text-sm">
          ← Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
