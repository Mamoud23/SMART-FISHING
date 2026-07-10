import { NavLink } from 'react-router-dom';
import { 
  HomeIcon, MapIcon, ChartBarIcon, 
  BellIcon, CogIcon, ServerIcon 
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Temps Réel', href: '/', icon: HomeIcon },
  { name: 'Carte', href: '/map', icon: MapIcon },
  { name: 'Historique', href: '/history', icon: ChartBarIcon },
  { name: 'Alertes', href: '/alerts', icon: BellIcon },
  { name: 'Métriques', href: '/metrics', icon: ServerIcon },
  { name: 'Administration', href: '/admin', icon: CogIcon },
];

const Sidebar = () => {
  return (
    <div className="w-64 bg-blue-900 text-white flex flex-col">
      <div className="p-4 border-b border-blue-800">
        <h1 className="text-xl font-bold">🐟 Smart Fishing</h1>
        <p className="text-sm text-blue-300">Suivi des pêches</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-4 py-2 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-blue-800 text-white' 
                  : 'hover:bg-blue-800 text-blue-200'
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-blue-800 text-xs text-blue-300">
        Version 1.0.0
      </div>
    </div>
  );
};

export default Sidebar;