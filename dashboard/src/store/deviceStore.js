// src/store/deviceStore.js
import { create } from 'zustand';

const useDeviceStore = create((set, get) => ({
  // État
  devices: [],
  loading: false,
  error: null,
  selectedDevice: null,
  deviceStatus: {},

  // Actions
  setDevices: (devices) => set({ devices }),
  
  addDevice: (device) => set((state) => ({ 
    devices: [...state.devices, device] 
  })),
  
  updateDevice: (id, data) => set((state) => ({
    devices: state.devices.map(d => 
      d.id === id ? { ...d, ...data } : d
    )
  })),
  
  removeDevice: (id) => set((state) => ({
    devices: state.devices.filter(d => d.id !== id)
  })),
  
  setSelectedDevice: (id) => set({ selectedDevice: id }),
  
  updateDeviceStatus: (id, status) => set((state) => ({
    devices: state.devices.map(d => 
      d.id === id ? { ...d, status } : d
    ),
    deviceStatus: {
      ...state.deviceStatus,
      [id]: status
    }
  })),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  // Getter
  getDeviceById: (id) => {
    return get().devices.find(d => d.id === id);
  },
  
  getOnlineDevices: () => {
    return get().devices.filter(d => d.status === 'online');
  },
  
  getAlertDevices: () => {
    return get().devices.filter(d => d.status === 'alert');
  },
  
  getOfflineDevices: () => {
    return get().devices.filter(d => d.status === 'offline');
  },
}));

export default useDeviceStore;