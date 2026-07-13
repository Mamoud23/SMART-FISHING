"""
Vérifie que le WebSocket /ws relaie bien les alertes SOS en temps réel.

Utilisation : ouvre DEUX terminaux.

Terminal 1 (écoute) :
    docker exec -it sf_tools python test_websocket.py

Terminal 2 (déclenche une alerte pendant que le terminal 1 écoute) :
    Crée une alerte via Swagger (POST /alertes-sos) ou avec insert_test_gps.py.

Tu dois voir le message apparaître dans le Terminal 1 quasi instantanément.
"""

import asyncio
import websockets

WS_URL = "ws://api:8000/ws"


async def ecouter():
    print(f"Connexion à {WS_URL}...")
    async with websockets.connect(WS_URL) as ws:
        print("Connecté. En attente d'alertes SOS (Ctrl+C pour arrêter)...\n")
        async for message in ws:
            print(f"[alerte reçue] {message}")


if __name__ == "__main__":
    asyncio.run(ecouter())