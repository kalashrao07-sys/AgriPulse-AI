import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Sprout, LayoutDashboard, MessageSquare, Leaf, CloudSun, Clock, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useFarm } from '../hooks/useFarm';
import clsx from 'clsx';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/advisor', label: 'AI Advisor', icon: MessageSquare },
  { to: '/crop-health', label: 'Crop Health', icon: Leaf },
  { to: '/weather', label: 'Weather', icon: CloudSun },
  { to: '/timeline', label: 'Farm Timeline', icon: Clock },
];

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { farm } = useFarm();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 bg-forest-900 text-white flex flex-col transition-transform duration-300',
        mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      )}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-forest-700">
          <div className="w-9 h-9 bg-forest-500 rounded-lg flex items-center justify-center">
            <Sprout className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-white text-lg leading-tight">AgriPulse</div>
            <div className="text-forest-300 text-xs">Smart Advice. Better Farming.</div>
          </div>
        </div>

        {/* Farm info */}
        {farm && (
          <div className="mx-4 mt-4 p-3 bg-forest-800 rounded-lg border border-forest-700">
            <div className="text-forest-300 text-xs uppercase tracking-wide mb-1">Active Farm</div>
            <div className="text-white font-medium text-sm">{farm.farmer_name}</div>
            <div className="text-forest-400 text-xs">{farm.crop_name} · {farm.location}</div>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-forest-600 text-white'
                  : 'text-forest-300 hover:bg-forest-800 hover:text-white'
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-forest-700">
          <button
            onClick={() => navigate('/setup')}
            className="w-full text-xs text-forest-400 hover:text-forest-200 text-left transition-colors"
          >
            ⚙ Farm Setup
          </button>
          <div className="text-forest-600 text-xs mt-1">AgriPulse AI v1.0</div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 md:ml-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 md:hidden sticky top-0 z-30">
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 rounded-lg hover:bg-gray-100"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <div className="flex items-center gap-2">
            <Sprout className="w-5 h-5 text-forest-600" />
            <span className="font-bold text-forest-800">AgriPulse</span>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
