"""
Simule les 7 capteurs d'un bateau en PUBLIANT SUR MQTT (pas en appelant l'API
directement) — contrairement à simulate_capteurs.py, ce script joue vraiment
le rôle du capteur physique dans le pipeline complet :

    ce script --MQTT--> Mosquitto --> Node-RED --> ton API/InfluxDB

Utile pour tester le sandbox iot-test/ (Mosquitto + Node-RED) de bout en bout.

⚠️ Seul le topic SOS a un flow Node-RED prêt (flows_sos.json). Les 6 autres
topics sont publiés normalement, mais ne seront traités que si des flows
Node-RED correspondants existent (cf. GUIDE_INTEGRATION_NODERED.md pour le
détail de chaque flow à construire).

Utilisation (depuis le conteneur sf_tools, sur le même réseau que mosquitto) :

    docker exec -it sf_tools python simulate_capteurs_mqtt.py <id_bateau> --vitesse 60

--vitesse 60 accélère le temps x60 (1 minute simulée = 1 seconde réelle).
Arrête avec Ctrl+C.
"""

import argparse
import json
import random
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883


def se_connecter() -> mqtt.Client:
    client = mqtt.Client()
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    return client


def publier(client: mqtt.Client, id_bateau: str, capteur: str, payload: dict):
    topic = f"fishing/boat/{id_bateau}/{capteur}"
    client.publish(topic, json.dumps(payload))
    print(f"[{capteur}] -> {topic} : {payload}")


def boucle_gps(client, id_bateau, intervalle, arret):
    lat, lng = 5.30, -4.00
    while not arret.is_set():
        lat += random.uniform(-0.003, 0.003)
        lng += random.uniform(-0.003, 0.003)
        publier(client, id_bateau, "gps", {
            "lat": round(lat, 5), "lng": round(lng, 5), "vitesse": round(random.uniform(4, 14), 1),
        })
        arret.wait(intervalle)


def boucle_temperature_eau(client, id_bateau, intervalle, arret):
    while not arret.is_set():
        publier(client, id_bateau, "water_temp", {"temp_celsius": round(random.uniform(24, 30), 1)})
        arret.wait(intervalle)


def boucle_vent(client, id_bateau, intervalle, arret):
    while not arret.is_set():
        vitesse = round(random.uniform(35, 45), 1) if random.random() < 0.1 else round(random.uniform(5, 20), 1)
        publier(client, id_bateau, "wind", {
            "vitesse_kmh": vitesse, "direction_deg": round(random.uniform(0, 359), 0),
        })
        arret.wait(intervalle)


def boucle_turbidite(client, id_bateau, intervalle, arret):
    while not arret.is_set():
        publier(client, id_bateau, "turbidity", {"ntu": round(random.uniform(2, 20), 1)})
        arret.wait(intervalle)


def boucle_inclinaison(client, id_bateau, intervalle, arret):
    while not arret.is_set():
        risque = random.random() < 0.03
        angle = round(random.uniform(40, 55), 1) if risque else round(random.uniform(0, 15), 1)
        publier(client, id_bateau, "tilt", {"angle_deg": angle, "risque_chavirement": risque})
        arret.wait(intervalle)


def boucle_captures(client, id_bateau, intervalle, arret):
    especes = ["Thon", "Capitaine", "Bar", "Dorade", "Carpe rouge"]
    while not arret.is_set():
        publier(client, id_bateau, "catch", {
            "espece": random.choice(especes),
            "poids_kg": round(random.uniform(1, 20), 1),
            "quantite": random.randint(1, 5),
            "gps_a_la_capture": {"lat": 5.30, "lng": -4.00},
        })
        arret.wait(intervalle)


def boucle_sos(client, id_bateau, intervalle, arret, probabilite: float):
    """SOS = événement rare, pas une fréquence fixe. On tire au sort à chaque tick."""
    while not arret.is_set():
        if random.random() < probabilite:
            publier(client, id_bateau, "sos", {
                "lat": round(5.30 + random.uniform(-0.05, 0.05), 5),
                "lng": round(-4.00 + random.uniform(-0.05, 0.05), 5),
            })
        arret.wait(intervalle)


def main():
    parser = argparse.ArgumentParser(description="Simule les 7 capteurs d'un bateau, publiés sur MQTT.")
    parser.add_argument("id_bateau", help="Id du bateau à simuler (récupérable via GET /bateaux)")
    parser.add_argument("--vitesse", type=float, default=1.0, help="Facteur d'accélération du temps (60 = 1min -> 1s)")
    parser.add_argument("--proba-sos", type=float, default=0.01, help="Probabilité de déclenchement SOS à chaque vérification (par défaut 1%%)")
    args = parser.parse_args()

    client = se_connecter()
    print(f"Connecté à {BROKER_HOST}:{BROKER_PORT}. Simulation MQTT du bateau {args.id_bateau} (vitesse x{args.vitesse})...\n")

    # Fréquences personnalisées (en secondes)
    frequences = {
        "gps": 5,
        "inclinaison": 5,
        "temperature_eau": 10,
        "vent": 10,
        "turbidite": 15,
        "captures": 30,
        "sos_check": 30,
    }


    arret = threading.Event()
    threads = [
        threading.Thread(target=boucle_gps, args=(client, args.id_bateau, frequences["gps"], arret), daemon=True),
        threading.Thread(target=boucle_temperature_eau, args=(client, args.id_bateau, frequences["temperature_eau"], arret), daemon=True),
        threading.Thread(target=boucle_vent, args=(client, args.id_bateau, frequences["vent"], arret), daemon=True),
        threading.Thread(target=boucle_turbidite, args=(client, args.id_bateau, frequences["turbidite"], arret), daemon=True),
        threading.Thread(target=boucle_inclinaison, args=(client, args.id_bateau, frequences["inclinaison"], arret), daemon=True),
        threading.Thread(target=boucle_captures, args=(client, args.id_bateau, frequences["captures"], arret), daemon=True),
        threading.Thread(target=boucle_sos, args=(client, args.id_bateau, frequences["sos_check"], arret, args.proba_sos), daemon=True),
    ]
    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArrêt de la simulation...")
        arret.set()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
