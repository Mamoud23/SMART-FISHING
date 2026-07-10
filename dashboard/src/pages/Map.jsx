import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import { useDevices } from '../hooks/useDevices';
import 'leaflet/dist/leaflet.css';

// Icône personnalisée
const createIcon = (status) => {
  const colors = {
    online: '#22C55E',
    alert: '#EF4444',
    offline: '#6B7280',
  };
  return new Icon({
    iconUrl: `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${colors[status]}"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
  });
};

const Map = () => {
  const { devices } = useDevices();
  const center = [5.36, -4.01]; // Coordonnées d'Abidjan

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">🗺️ Carte des Bateaux</h1>
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="h-[600px]">
          <MapContainer center={center} zoom={11} className="h-full w-full rounded-lg">
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            {devices.map((device) => (
              <Marker
                key={device.id}
                position={[device.latitude || 5.36, device.longitude || -4.01]}
                icon={createIcon(device.status)}
              >
                <Popup>
                  <div className="text-sm">
                    <h3 className="font-bold">{device.name}</h3>
                    <p>Statut: <span className={`font-semibold ${
                      device.status === 'online' ? 'text-green-600' : 
                      device.status === 'alert' ? 'text-red-600' : 'text-gray-500'
                    }`}>{device.status}</span></p>
                    <p>Temp: {device.waterTemp || 'N/A'}°C</p>
                    <p>Captures: {device.catches || 0} kg</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
};

export default Map;