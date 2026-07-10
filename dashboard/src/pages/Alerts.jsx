import { useState } from 'react';
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const Alerts = () => {
  const [alerts, setAlerts] = useState([
    { id: 1, device: 'Bateau 001', type: 'Chavirement', message: 'Détection d\'inclinaison anormale', time: '14:30', status: 'active' },
    { id: 2, device: 'Bateau 002', type: 'SOS', message: 'Bouton d\'urgence activé', time: '14:15', status: 'active' },
    { id: 3, device: 'Bateau 003', type: 'Position', message: 'Hors de la zone de pêche', time: '13:45', status: 'resolved' },
  ]);

  const acknowledgeAlert = (id) => {
    setAlerts(alerts.map(a => 
      a.id === id ? { ...a, status: 'resolved' } : a
    ));
  };

  const activeAlerts = alerts.filter(a => a.status === 'active');
  const resolvedAlerts = alerts.filter(a => a.status === 'resolved');

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">🔔 Alertes & Incidents</h1>
      
      {/* Alertes Actives */}
      <div>
        <h2 className="text-lg font-semibold text-red-600 flex items-center">
          <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
          Alertes Actives ({activeAlerts.length})
        </h2>
        <div className="space-y-3 mt-3">
          {activeAlerts.map((alert) => (
            <div key={alert.id} className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500 flex justify-between items-center">
              <div>
                <p className="font-bold">{alert.device}</p>
                <p className="text-sm text-gray-600">{alert.type}: {alert.message}</p>
                <p className="text-xs text-gray-400">{alert.time}</p>
              </div>
              <button
                onClick={() => acknowledgeAlert(alert.id)}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
              >
                Acquitter
              </button>
            </div>
          ))}
          {activeAlerts.length === 0 && (
            <p className="text-gray-500">Aucune alerte active</p>
          )}
        </div>
      </div>

      {/* Historique des Alertes */}
      <div>
        <h2 className="text-lg font-semibold text-gray-600 flex items-center">
          <CheckCircleIcon className="w-5 h-5 mr-2" />
          Historique ({resolvedAlerts.length})
        </h2>
        <div className="space-y-2 mt-3">
          {resolvedAlerts.map((alert) => (
            <div key={alert.id} className="bg-gray-50 p-3 rounded-lg flex justify-between items-center opacity-75">
              <div>
                <p className="font-medium">{alert.device}</p>
                <p className="text-sm text-gray-600">{alert.type}: {alert.message}</p>
                <p className="text-xs text-gray-400">{alert.time}</p>
              </div>
              <span className="text-sm text-green-600">✓ Résolu</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Alerts;