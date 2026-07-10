// src/hooks/useWebSocket.js
import { useEffect, useState, useCallback } from 'react';
import websocketService from '../services/websocket';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [lastAlert, setLastAlert] = useState(null);

  useEffect(() => {
    // Connexion WebSocket
    websocketService.connect();

    // Vérifier l'état de connexion
    setIsConnected(websocketService.isConnected());

    // Écouter les événements
    const handleData = (data) => {
      setLastMessage(data);
    };

    const handleAlert = (alert) => {
      setLastAlert(alert);
    };

    websocketService.addListener('device:data', handleData);
    websocketService.addListener('device:alert', handleAlert);

    // Vérifier périodiquement la connexion
    const interval = setInterval(() => {
      setIsConnected(websocketService.isConnected());
    }, 5000);

    return () => {
      websocketService.removeListener('device:data', handleData);
      websocketService.removeListener('device:alert', handleAlert);
      clearInterval(interval);
      websocketService.disconnect();
    };
  }, []);

  // Fonction pour émettre des données
  const emit = useCallback((event, data) => {
    websocketService.emit(event, data);
  }, []);

  return {
    isConnected,
    lastMessage,
    lastAlert,
    emit,
  };
};