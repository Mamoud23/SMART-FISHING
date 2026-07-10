// src/pages/Realtime.jsx
import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useDevices } from '../hooks/useDevices';
import DeviceCard from '../components/Cards/DeviceCard';
import StatCard from '../components/Cards/StatCard';

const Realtime = () => {
  const { devices, loading } = useDevices();
  const [realtimeData, setRealtimeData] = useState([]);

  // Simuler des données en temps réel
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const time = now.toTimeString().slice(0, 8);
      
      const newData = {
        time: time,
        temperature: 25 + Math.random() * 6,
        windSpeed: 8 + Math.random() * 18,
        catches: Math.floor(15 + Math.random() * 40),
      };
      
      setRealtimeData(prev => {
        const newDataArray = [...prev, newData];
        // Garder seulement les 30 derniers points
        if (newDataArray.length > 30) {
          return newDataArray.slice(-30);
        }
        return newDataArray;
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Statistiques
  const stats = {
    total: devices.length,
    online: devices.filter(d => d.status === 'online').length,
    alert: devices.filter(d => d.status === 'alert').length,
    offline: devices.filter(d => d.status === 'offline').length,
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">📡 Données en Temps Réel</h1>
        <div className="flex items-center space-x-2 text-sm">
          <span className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
            Live
          </span>
          <span className="text-gray-400">|</span>
          <span className="text-gray-500">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
      
      {/* Statistiques */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          label="Total Bateaux" 
          value={stats.total} 
          color="blue"
          icon="🚢"
        />
        <StatCard 
          label="En Ligne" 
          value={stats.online} 
          color="green"
          icon="🟢"
        />
        <StatCard 
          label="Alertes" 
          value={stats.alert} 
          color="red"
          icon="🔴"
        />
        <StatCard 
          label="Hors Ligne" 
          value={stats.offline} 
          color="gray"
          icon="⚫"
        />
      </div>

      {/* Graphique en temps réel */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">📈 Évolution des Mesures</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={realtimeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 11 }}
              interval={2}
            />
            <YAxis 
              yAxisId="left" 
              tick={{ fontSize: 11 }}
              domain={[0, 50]}
            />
            <YAxis 
              yAxisId="right" 
              orientation="right"
              tick={{ fontSize: 11 }}
              domain={[0, 50]}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '12px',
                padding: '8px 12px'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
            />
            <Line 
              yAxisId="left" 
              type="monotone" 
              dataKey="temperature" 
              stroke="#3B82F6" 
              name="🌡️ Température (°C)" 
              strokeWidth={2}
              dot={false}
            />
            <Line 
              yAxisId="left" 
              type="monotone" 
              dataKey="windSpeed" 
              stroke="#10B981" 
              name="💨 Vent (km/h)" 
              strokeWidth={2}
              dot={false}
            />
            <Line 
              yAxisId="right" 
              type="monotone" 
              dataKey="catches" 
              stroke="#F59E0B" 
              name="🐟 Captures (kg)" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Liste des bateaux */}
      <div>
        <h2 className="text-lg font-semibold text-gray-700 mb-4">🛥️ Bateaux Actifs</h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {devices.slice(0, 6).map((device) => (
              <DeviceCard key={device.id} device={device} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Realtime;