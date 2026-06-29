import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  BookOpen,
  Database,
  Cpu,
  Calculator,
  Briefcase,
  BarChart3,
  Settings,
  Flame,
  Star,
  Menu,
  X,
} from 'lucide-react';
import { useState } from 'react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
  { name: 'ADSA', href: '/subjects/adsa', icon: BookOpen },
  { name: 'DBMS', href: '/subjects/dbms', icon: Database },
  { name: 'COA', href: '/subjects/coa', icon: Cpu },
  { name: 'Probability', href: '/subjects/probability', icon: Calculator },
  { name: 'AMCAT', href: '/amcat', icon: Briefcase },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Layout() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-900/80" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 w-64 bg-gray-800">
          <div className="flex h-16 items-center justify-between px-6 border-b border-gray-700">
            <span className="text-xl font-bold text-primary-400">S3OS</span>
            <button onClick={() => setSidebarOpen(false)}>
              <X className="w-6 h-6 text-gray-400" />
            </button>
          </div>
          <nav className="mt-6 px-3">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg mb-1 transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 bg-gray-800">
          <div className="flex h-16 items-center px-6 border-b border-gray-700">
            <span className="text-2xl font-bold text-primary-400">S3OS</span>
            <span className="ml-2 text-xs text-gray-400">Academic OS</span>
          </div>
          <nav className="flex-1 mt-6 px-3 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg mb-1 transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          {/* User info */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold">
                S3
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  Semester 3
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Star className="w-3 h-3" />
                  <span>BE Computer</span>
                  <Flame className="w-3 h-3 text-orange-500" />
                  <span>CU</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <div className="sticky top-0 z-40 flex h-16 items-center gap-4 px-4 bg-gray-900 border-b border-gray-800 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 text-gray-400 hover:text-white"
          >
            <Menu className="w-6 h-6" />
          </button>
          <span className="text-lg font-semibold text-white">S3OS</span>
        </div>

        <main className="min-h-screen p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
