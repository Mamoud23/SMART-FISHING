import { useState } from 'react';

const Admin = () => {
  const [devices, setDevices] = useState([
    { id: 'boat-001', name: 'Bateau 001', status: 'online', threshold: 30 },
    { id: 'boat-002', name: 'Bateau 002', status: 'online', threshold: 25 },
    { id: 'boat-003', name: 'Bateau 003', status: 'alert', threshold: 20 },
  ]);

  const [newDevice, setNewDevice] = useState({ name: '', threshold: 30 });

  const addDevice = (e) => {
    e.preventDefault();
    setDevices([...devices, { 
      id: `boat-${String(devices.length + 1).padStart(3, '0')}`, 
      ...newDevice, 
      status: 'online' 
    }]);
    setNewDevice({ name: '', threshold: 30 });
  };

  const deleteDevice = (id) => {
    setDevices(devices.filter(d => d.id !== id));
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">⚙️ Administration</h1>

      {/* Ajouter un bateau */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Ajouter un Bateau</h2>
        <form onSubmit={addDevice} className="flex space-x-4">
          <input
            type="text"
            placeholder="Nom du bateau"
            className="flex-1 border rounded px-3 py-2"
            value={newDevice.name}
            onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Seuil (°C)"
            className="w-32 border rounded px-3 py-2"
            value={newDevice.threshold}
            onChange={(e) => setNewDevice({ ...newDevice, threshold: parseInt(e.target.value) })}
            required
          />
          <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Ajouter
          </button>
        </form>
      </div>

      {/* Liste des bateaux */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Seuil</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {devices.map((device) => (
              <tr key={device.id}>
                <td className="px-6 py-4 text-sm">{device.id}</td>
                <td className="px-6 py-4 text-sm font-medium">{device.name}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    device.status === 'online' ? 'bg-green-100 text-green-800' :
                    device.status === 'alert' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {device.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">{device.threshold}°C</td>
                <td className="px-6 py-4 text-sm">
                  <button
                    onClick={() => deleteDevice(device.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Admin;