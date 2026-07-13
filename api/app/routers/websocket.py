"""
Relaie en temps réel les alertes SOS vers le dashboard, via WebSocket.

Principe : chaque connexion WebSocket s'abonne au canal Redis Pub/Sub
"sos:alertes" (déjà utilisé par cache_aside.publish_sos_alert lors de la
création d'une alerte). Dès qu'un message est publié sur ce canal, il est
immédiatement transmis au client connecté.

Le client Redis existant (redis_client.py) est synchrone (Sentinel), donc on
interroge pubsub.get_message() dans un thread séparé (run_in_executor) pour
ne pas bloquer la boucle d'événements asyncio de FastAPI.
"""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from redis_client import get_redis_replica

router = APIRouter()


@router.websocket("/ws")
async def websocket_alertes_sos(websocket: WebSocket):
    await websocket.accept()

    redis_conn = get_redis_replica()
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("sos:alertes")

    loop = asyncio.get_event_loop()

    try:
        while True:
            message = await loop.run_in_executor(
                None,
                lambda: pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0),
            )
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[websocket] Erreur, fermeture de la connexion : {e}")
    finally:
        pubsub.close()