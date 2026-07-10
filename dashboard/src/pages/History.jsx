import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const History = () => {
  const [period, setPeriod] = useState('24h');
  const [selectedDevice, setSelectedDevice] = useState('all');

  // Données mock
  const mockData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}h`,
    temperature: 25 + Math.random() * 5,
    windSpeed: 10 + Math.random() * 15,
    catches: Math.floor(Math.random() * 50),
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">📊 Historique & Tendances</h1>
      
      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow flex items-center space-x-4">
        <div>
          <label className="text-sm text-gray-600">Période</label>
          <select 
            className="ml-2 border rounded px-3 py-1"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <option value="1h">1 Heure</option>
            <option value="6h">6 Heures</option>
            <option value="24h">24 Heures</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-gray-600">Bateau</label>
          <select 
            className="ml-2 border rounded px-3 py-1"
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
          >
            <option value="all">Tous</option>
            <option value="boat-001">Bateau 001</option>
            <option value="boat-002">Bateau 002</option>
            <option value="boat-003">Bateau 003</option>
          </select>
        </div>
      </div>

      {/* Graphique */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Tendances sur {period}</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={mockData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="temperature" stroke="#3B82F6" name="Température (°C)" />
            <Line yAxisId="left" type="monotone" dataKey="windSpeed" stroke="#10B981" name="Vent (km/h)" />
            <Line yAxisId="right" type="monotone" dataKey="catches" stroke="#F59E0B" name="Captures (kg)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">Température Moyenne</p>
          <p className="text-2xl font-bold">26.5°C</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">Vent Moyen</p>
          <p className="text-2xl font-bold">18.7 km/h</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">Captures Totales</p>
          <p className="text-2xl font-bold">342 kg</p>
        </div>
      </div>
    </div>
  );
};

export default History;