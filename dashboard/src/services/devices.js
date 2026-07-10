// src/services/devices.js
import api from './api';

// Récupérer tous les devices
export const getDevices = async () => {
  try {
    // Si l'API est disponible
    // const response = await api.get('/devices');
    // return response.data;
    
    // Données mock pour le développement
    return mockDevices();
  } catch (error) {
    console.error('Erreur lors du chargement des devices:', error);
    return mockDevices(); // Fallback sur les données mock
  }
};

// Récupérer un device par ID
export const getDeviceById = async (id) => {
  try {
    // const response = await api.get(`/devices/${id}`);
    // return response.data;
    
    const devices = mockDevices();
    return devices.find(d => d.id === id);
  } catch (error) {
    console.error(`Erreur lors du chargement du device ${id}:`, error);
    return null;
  }
};

// Mettre à jour un device
export const updateDevice = async (id, data) => {
  try {
    // const response = await api.put(`/devices/${id}`, data);
    // return response.data;
    console.log(`Device ${id} mis à jour avec:`, data);
    return { id, ...data };
  } catch (error) {
    console.error(`Erreur lors de la mise à jour du device ${id}:`, error);
    throw error;
  }
};

// Supprimer un device
export const deleteDevice = async (id) => {
  try {
    // const response = await api.delete(`/devices/${id}`);
    // return response.data;
    console.log(`Device ${id} supprimé`);
    return { success: true };
  } catch (error) {
    console.error(`Erreur lors de la suppression du device ${id}:`, error);
    throw error;
  }
};

// Données mock pour le développement
const mockDevices = () => {
  return [
    { 
      id: 'boat-001', 
      name: 'Bateau 001', 
      status: 'online', 
      latitude: 5.36, 
      longitude: -4.01, 
      waterTemp: 27.5, 
      catches: 45, 
      windSpeed: 12, 
      lastUpdate: '14:30' 
    },
    { 
      id: 'boat-002', 
      name: 'Bateau 002', 
      status: 'online', 
      latitude: 5.32, 
      longitude: -4.05, 
      waterTemp: 26.8, 
      catches: 32, 
      windSpeed: 15, 
      lastUpdate: '14:28' 
    },
    { 
      id: 'boat-003', 
      name: 'Bateau 003', 
      status: 'alert', 
      latitude: 5.40, 
      longitude: -3.98, 
      waterTemp: 28.2, 
      catches: 0, 
      windSpeed: 8, 
      lastUpdate: '14:25' 
    },
    { 
      id: 'boat-004', 
      name: 'Bateau 004', 
      status: 'offline', 
      latitude: 5.30, 
      longitude: -4.10, 
      waterTemp: null, 
      catches: null, 
      windSpeed: null, 
      lastUpdate: '12:00' 
    },
    { 
      id: 'boat-005', 
      name: 'Bateau 005', 
      status: 'online', 
      latitude: 5.45, 
      longitude: -3.95, 
      waterTemp: 26.2, 
      catches: 28, 
      windSpeed: 18, 
      lastUpdate: '14:32' 
    },
    { 
      id: 'boat-006', 
      name: 'Bateau 006', 
      status: 'alert', 
      latitude: 5.25, 
      longitude: -4.15, 
      waterTemp: 29.1, 
      catches: 0, 
      windSpeed: 5, 
      lastUpdate: '14:20' 
    },
  ];
};