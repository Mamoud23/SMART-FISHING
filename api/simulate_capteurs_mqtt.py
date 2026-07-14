#!/usr/bin/env python3
"""
Simule les 7 capteurs d'un bateau en PUBLIANT SUR MQTT.

Correctifs par rapport à la v2 :
  1. Détection de port via socket brut (pas via mqtt.Client().connect(),
     qui n'accepte pas de paramètre timeout et cassait la détection).
  2. Vérification RÉELLE de la connexion : on attend le CONNACK via
     on_connect avant de démarrer les capteurs. Si l'auth échoue
     (mauvais user/mdp), le script l'affiche clairement et s'arrête —
     il ne part plus "à l'aveugle".
  3. Host / user / mot de passe / certificat configurables en CLI ou
     variables d'environnement, plus besoin d'éditer le fichier pour
     changer de broker.

Usage (broker vulnérable, port 1883, détection auto) :
    docker exec -it sf_tools python simulate_capteurs_mqtt.py <id_bateau>

Usage (broker sécurisé, port 8883, TLS + user/mdp) :
    docker exec -it sf_tools python simulate_capteurs_mqtt.py <id_bateau> --user capteur_temp

Variables d'environnement possibles (évite de taper les secrets en clair) :
    MQTT_HOST, MQTT_USER, MQTT_PASSWORD, MQTT_CA_CERT
"""

import argparse
import getpass
import json
import os
import random
import socket
import ssl
import sys
import threading
import time

import paho.mqtt.client as mqtt

DEFAULT_HOST = os.environ.get("MQTT_HOST", "localhost")
DEFAULT_CA_CERT = os.environ.get("MQTT_CA_CERT", "/etc/mosquitto/ca.crt")
CONNECT_TIMEOUT_S = 5  # temps max pour obtenir le CONNACK


def port_ouvert(host: str, port: int, timeout: float = 2.0) -> bool:
    """Teste juste si un port TCP répond, sans se soucier du protocole applicatif."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def se_connecter(host: str, args) -> mqtt.Client:
    """
    Choisit le bon mode de connexion selon le port ouvert, puis attend
    la confirmation réelle (CONNACK) avant de rendre la main. Quitte
    proprement si la connexion/authentification échoue.
    """
    connecte = threading.Event()
    echec = {"rc": None}

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            connecte.set()
        else:
            echec["rc"] = rc
            connecte.set()

    if port_ouvert(host, 1883):
        print(f"[*] Port 1883 ouvert sur {host} -> broker vulnérable (connexion anonyme)")
        client = mqtt.Client()
        client.on_connect = on_connect
        client.connect(host, 1883, keepalive=60)

    elif port_ouvert(host, 8883):
        print(f"[*] Port 8883 ouvert sur {host} -> broker sécurisé (TLS + authentification)")
        username = args.user or input("Nom d'utilisateur : ")
        password = args.password or getpass.getpass("Mot de passe : ")

        client = mqtt.Client()
        client.username_pw_set(username, password)
        client.tls_set(
            ca_certs=args.ca_cert,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
        )
        client.on_connect = on_connect
        client.connect(host, 8883, keepalive=60)

    else:
        print(f"[-] Aucun broker joignable sur {host}:1883 ni {host}:8883")
        print("[*] Vérifie que Mosquitto/EMQX est lancé et que le host est correct")
        print(f"    (host utilisé : '{host}' — sur Docker c'est souvent le nom du service, pas 'localhost')")
        sys.exit(1)

    client.loop_start()

    if not connecte.wait(timeout=CONNECT_TIMEOUT_S):
        print("[-] Timeout : pas de réponse du broker (CONNACK jamais reçu)")
        client.loop_stop()
        sys.exit(1)

    if echec["rc"] is not None:
        print(f"[-] Connexion refusée par le broker (code retour {echec['rc']}) — "
              f"vérifie le nom d'utilisateur / mot de passe / certificat")
        client.loop_stop()
        sys.exit(1)

    print("[+] Connecté et authentifié avec succès.\n")
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
    while not arret.is_set():
        if random.random() < probabilite:
            publier(client, id_bateau, "sos", {
                "lat": round(5.30 + random.uniform(-0.05, 0.05), 5),
                "lng": round(-4.00 + random.uniform(-0.05, 0.05), 5),
            })
        arret.wait(intervalle)


def main():
    parser = argparse.ArgumentParser(description="Simule les 7 capteurs d'un bateau, publiés sur MQTT.")
    parser.add_argument("id_bateau", help="Id du bateau à simuler")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host du broker (défaut: {DEFAULT_HOST}, ou variable MQTT_HOST)")
    parser.add_argument("--user", default=os.environ.get("MQTT_USER"), help="Nom d'utilisateur (broker sécurisé)")
    parser.add_argument("--password", default=os.environ.get("MQTT_PASSWORD"), help="Mot de passe (broker sécurisé)")
    parser.add_argument("--ca-cert", default=DEFAULT_CA_CERT, help=f"Chemin du certificat CA (défaut: {DEFAULT_CA_CERT})")
    parser.add_argument("--proba-sos", type=float, default=0.01, help="Probabilité de déclenchement SOS (défaut 1%%)")
    args = parser.parse_args()

    client = se_connecter(args.host, args)
    print(f"Simulation du bateau {args.id_bateau} en cours...\n")

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
