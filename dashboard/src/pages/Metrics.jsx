import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Metrics = () => {
  const [systemMetrics, setSystemMetrics] = useState([]);

  useEffect(() => {
    // Simuler des métriques système
    const interval = setInterval(() => {
      const now = new Date();
      setSystemMetrics(prev => [...prev.slice(-20), {
        time: `${now.getHours()}:${now.getMinutes()}`,
        cpu: 20 + Math.random() * 60,
        memory: 30 + Math.random() * 50,
        latency: 50 + Math.random() * 200,
        cacheHit: 60 + Math.random() * 35,
      }]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Intégration Grafana (iframe)
  const grafanaUrl = 'http://localhost:3000/d/iot-dashboard?kiosk';

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">📈 Métriques Système</h1>

      {/* Métriques en temps réel */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Performance Système</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={systemMetrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis yAxisId="left" domain={[0, 100]} />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="cpu" stroke="#EF4444" name="CPU (%)" />
            <Line yAxisId="left" type="monotone" dataKey="memory" stroke="#3B82F6" name="RAM (%)" />
            <Line yAxisId="right" type="monotone" dataKey="cacheHit" stroke="#10B981" name="Cache Hit Rate (%)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Métriques actuelles */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">CPU</p>
          <p className="text-2xl font-bold text-red-600">45%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">RAM</p>
          <p className="text-2xl font-bold text-blue-600">62%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">Cache Hit Rate</p>
          <p className="text-2xl font-bold text-green-600">78%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-500">Latence API</p>
          <p className="text-2xl font-bold text-yellow-600">124ms</p>
        </div>
      </div>

      {/* Dashboard Grafana intégré */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">📊 Dashboard Grafana</h2>
        <div className="h-[500px] border rounded-lg overflow-hidden">
          <iframe
            src={grafanaUrl}
            className="w-full h-full"
            title="Grafana Dashboard"
          />
        </div>
      </div>
    </div>
  );
};

export default Metrics;