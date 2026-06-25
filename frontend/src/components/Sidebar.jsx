import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Server, Lightbulb, AlertTriangle, TrendingUp, LogOut } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export default function Sidebar() {
  const { user, logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Resources', path: '/resources', icon: Server },
    { name: 'Recommendations', path: '/recommendations', icon: Lightbulb },
    { name: 'Anomalies', path: '/anomalies', icon: AlertTriangle },
    { name: 'Forecast', path: '/forecast', icon: TrendingUp },
  ];

  return (
    <div className="w-64 bg-bg-secondary border-r border-border h-screen flex flex-col hidden md:flex">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-accent tracking-wider">CloudCost</h1>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-accent/10 text-accent font-medium' 
                  : 'text-text-muted hover:text-text-primary hover:bg-bg-primary'
              }`
            }
          >
            <item.icon size={20} />
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="text-sm text-text-muted mb-4 px-4 truncate">
          {user?.sub || 'user@example.com'}
        </div>
        <button 
          onClick={logout}
          className="flex items-center gap-3 px-4 py-2 w-full text-text-muted hover:text-red-500 transition-colors"
        >
          <LogOut size={20} />
          Logout
        </button>
      </div>
    </div>
  );
}