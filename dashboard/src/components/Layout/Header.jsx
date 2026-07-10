// src/components/Layout/Header.jsx
import { useState } from 'react';
import { MagnifyingGlassIcon, UserCircleIcon, BellIcon as BellOutline } from '@heroicons/react/24/outline';

const Header = () => {
  const [search, setSearch] = useState('');

  return (
    <header className="bg-white shadow-sm px-6 py-3 flex items-center justify-between border-b border-gray-200">
      <div className="flex-1 flex items-center">
        <div className="relative w-80">
          <input
            type="text"
            placeholder="Rechercher un bateau..."
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <MagnifyingGlassIcon className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button className="relative p-1.5 text-gray-400 hover:text-gray-600 transition-colors">
          <BellOutline className="w-5 h-5" />
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="flex items-center space-x-3 border-l pl-4 border-gray-200">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-700">Admin</p>
            <p className="text-xs text-gray-500">Superviseur</p>
          </div>
          <UserCircleIcon className="w-8 h-8 text-gray-400" />
        </div>
      </div>
    </header>
  );
};

export default Header;