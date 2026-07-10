// src/hooks/useDevices.js
import { useState, useEffect } from 'react';
import { getDevices, updateDevice, deleteDevice } from '../services/devices';
import useDeviceStore from '../store/deviceStore';

export const useDevices = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Utiliser le store Zustand
  const { 
    devices, 
    setDevices, 
    updateDevice: updateDeviceStore,
    removeDevice,
    updateDeviceStatus
  } = useDeviceStore();

  // Charger les devices
  useEffect(() => {
    const loadDevices = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getDevices();
        setDevices(data);
      } catch (err) {
        setError(err.message || 'Erreur lors du chargement des devices');
        console.error('Erreur:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDevices();
  }, [setDevices]);

  // Mettre à jour un device
  const updateDeviceHandler = async (id, data) => {
    try {
      const updated = await updateDevice(id, data);
      updateDeviceStore(id, updated);
      return updated;
    } catch (error) {
      console.error('Erreur lors de la mise à jour:', error);
      throw error;
    }
  };

  // Supprimer un device
  const deleteDeviceHandler = async (id) => {
    try {
      await deleteDevice(id);
      removeDevice(id);
      return true;
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      throw error;
    }
  };

  // Mettre à jour le statut
  const updateStatus = (id, status) => {
    updateDeviceStatus(id, status);
  };

  // Récupérer le statut d'un device
  const getDeviceStatus = (id) => {
    const device = devices.find(d => d.id === id);
    return device ? device.status : 'unknown';
  };

  return {
    devices,
    loading,
    error,
    updateDevice: updateDeviceHandler,
    deleteDevice: deleteDeviceHandler,
    updateStatus,
    getDeviceStatus,
  };
};