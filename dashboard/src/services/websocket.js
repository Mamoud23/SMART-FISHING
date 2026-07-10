// src/services/websocket.js
import { io } from 'socket.io-client';

// Attention : pas de suffixe type "/ws" ici. Avec Socket.IO, tout ce qui suit
// l'origine dans l'URL est interprete comme un NAMESPACE, pas un chemin.
// On passe juste l'origine (protocole + host + port), le protocole /socket.io/
// est gere en interne par la librairie.
const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  // Initialiser la connexion WebSocket
  connect() {
    if (this.socket) {
      console.log('WebSocket déjà connecté');
      return;
    }

    try {
      this.socket = io(WS_URL, {
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      this.socket.on('connect', () => {
        console.log('🔌 WebSocket connecté');
        this.emit('device:connect', { client: 'dashboard' });
      });

      this.socket.on('disconnect', () => {
        console.log('🔌 WebSocket déconnecté');
      });

      this.socket.on('connect_error', (error) => {
        console.error('❌ Erreur de connexion WebSocket:', error);
      });

      // Écouter les événements de données
      this.socket.on('device:data', (data) => {
        this.notifyListeners('device:data', data);
      });

      this.socket.on('device:alert', (alert) => {
        this.notifyListeners('device:alert', alert);
      });

      this.socket.on('device:status', (status) => {
        this.notifyListeners('device:status', status);
      });

    } catch (error) {
      console.error('❌ Erreur lors de la connexion WebSocket:', error);
    }
  }

  // Déconnecter
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('🔌 WebSocket déconnecté manuellement');
    }
  }

  // Émettre un événement
  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('⚠️ WebSocket non connecté, impossible d\'émettre:', event);
    }
  }

  // Ajouter un écouteur
  addListener(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  // Supprimer un écouteur
  removeListener(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index !== -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  // Notifier tous les écouteurs d'un événement
  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Erreur dans le listener ${event}:`, error);
        }
      });
    }
  }

  // Vérifier si connecté
  isConnected() {
    return this.socket && this.socket.connected;
  }
}

// Singleton
const websocketService = new WebSocketService();
export default websocketService;