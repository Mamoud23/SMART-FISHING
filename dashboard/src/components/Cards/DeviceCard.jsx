// src/components/Cards/DeviceCard.jsx
const DeviceCard = ({ device }) => {
  const statusColors = {
    online: 'border-green-500 bg-green-50',
    alert: 'border-red-500 bg-red-50',
    offline: 'border-gray-400 bg-gray-50',
  };

  const statusText = {
    online: '🟢 En ligne',
    alert: '🔴 Alerte',
    offline: '⚫ Hors ligne',
  };

  return (
    <div className={`border-l-4 p-4 rounded-xl shadow-sm bg-white ${statusColors[device.status] || statusColors.offline}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-gray-800">{device.name}</h3>
          <p className="text-xs text-gray-500">{device.id}</p>
        </div>
        <span className="text-xs font-medium px-2 py-1 rounded-full bg-white/50">
          {statusText[device.status]}
        </span>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div className="bg-white/50 rounded-lg p-2">
          <p className="text-xs text-gray-500">🌡️ Température</p>
          <p className="font-semibold text-gray-800">{device.waterTemp || '--'}°C</p>
        </div>
        <div className="bg-white/50 rounded-lg p-2">
          <p className="text-xs text-gray-500">🐟 Captures</p>
          <p className="font-semibold text-gray-800">{device.catches || '--'} kg</p>
        </div>
        <div className="bg-white/50 rounded-lg p-2">
          <p className="text-xs text-gray-500">💨 Vent</p>
          <p className="font-semibold text-gray-800">{device.windSpeed || '--'} km/h</p>
        </div>
        <div className="bg-white/50 rounded-lg p-2">
          <p className="text-xs text-gray-500">🕐 MAJ</p>
          <p className="font-semibold text-gray-800 text-xs">{device.lastUpdate || '--'}</p>
        </div>
      </div>
    </div>
  );
};

export default DeviceCard;