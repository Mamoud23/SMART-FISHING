#!/usr/bin/env python3
"""
Test du spoofing sur le broker sécurisé — DOIT ÉCHOUER
"""

import paho.mqtt.client as mqtt
import ssl
import json
import time
import random

BROKER = "localhost"
PORT = 8883
USERNAME = "capteur_temp"
PASSWORD = "Smart-Fishing"
CA_CERT = "/etc/mosquitto/ca.crt"

CLIENT_ID = "capteur_GPS_001"
TOPIC = "fishing/boat/BT-Abi-01/gps"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[+] Connecté au broker sécurisé (TLS) ✅")
    else:
        print(f"[-] Échec de connexion, code: {rc}")

client = mqtt.Client(client_id=CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(ca_certs=CA_CERT, cert_reqs=ssl.CERT_REQUIRED)
client.on_connect = on_connect

print("[*] Tentative de spoofing sur le broker sécurisé (port 8883)...")
client.connect(BROKER, PORT, 60)
client.loop_start()
time.sleep(1)

for i in range(3):
    payload = {
        "capteur_id": "GPS-001",
        "lat": round(random.uniform(4.0, 4.5), 5),
        "lng": round(random.uniform(-8.0, -7.5), 5),
        "vitesse": round(random.uniform(0, 2), 1),
        "alerte": "POSITION_ANORMALE",
        "source": "spoofing"
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"[{i+1}/3] Publié: lat={payload['lat']}, lng={payload['lng']}")
    time.sleep(2)

client.loop_stop()
client.disconnect()
print("[+] Test terminé")
