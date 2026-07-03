#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time

# Configuration du proxy MITM
BROKER = "localhost"
PORT = 1884  # ← Le proxy écoute sur le port 1884

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[+] Connecté au proxy MITM ✅")

client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    payload = {
        "capteur_id": "TEMP-001",
        "valeur": 25.5,
        "unite": "C"
    }
    client.publish("test/mitm", json.dumps(payload))
    print(f"[+] Publié: {payload}")
    time.sleep(5)
