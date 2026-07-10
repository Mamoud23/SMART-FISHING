"""
Smart Fishing - API stub
Sert de backend temporaire pour debloquer le dashboard React (Frontend & Observabilite).
Le BD-GL n1 remplacera la logique interne (InfluxDB/MongoDB reelles, JWT, etc.)
sans que le frontend n'ait a changer un seul appel : le contrat REST/WS ci-dessous
est deja celui utilise par src/services/devices.js et src/services/websocket.js.
"""
import asyncio
import os
import random
import time
from datetime import datetime, timezone

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUX_ORG", "smart-fishing")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "fishing")

# ---------------------------------------------------------------------------
# FastAPI + Socket.IO (compatible avec socket.io-client cote React)
# ---------------------------------------------------------------------------
app = FastAPI(title="Smart Fishing API (stub)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hackathon: a restreindre en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)  # path par defaut: /socket.io/

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ---------------------------------------------------------------------------
# Etat en memoire (remplace ici par InfluxDB/MongoDB reels plus tard)
# ---------------------------------------------------------------------------
devices = [
    {"id": "boat-001", "name": "Bateau 001", "status": "online", "latitude": 5.36, "longitude": -4.01,
     "waterTemp": 27.5, "catches": 45, "windSpeed": 12, "threshold": 30},
    {"id": "boat-002", "name": "Bateau 002", "status": "online", "latitude": 5.32, "longitude": -4.05,
     "waterTemp": 26.8, "catches": 32, "windSpeed": 15, "threshold": 25},
    {"id": "boat-003", "name": "Bateau 003", "status": "alert", "latitude": 5.40, "longitude": -3.98,
     "waterTemp": 28.2, "catches": 0, "windSpeed": 8, "threshold": 20},
    {"id": "boat-004", "name": "Bateau 004", "status": "offline", "latitude": 5.30, "longitude": -4.10,
     "waterTemp": None, "catches": None, "windSpeed": None, "threshold": 30},
    {"id": "boat-005", "name": "Bateau 005", "status": "online", "latitude": 5.45, "longitude": -3.95,
     "waterTemp": 26.2, "catches": 28, "windSpeed": 18, "threshold": 30},
    {"id": "boat-006", "name": "Bateau 006", "status": "alert", "latitude": 5.25, "longitude": -4.15,
     "waterTemp": 29.1, "catches": 0, "windSpeed": 5, "threshold": 30},
]

alerts = [
    {"id": 1, "device": "Bateau 003", "type": "Position", "message": "Hors de la zone de peche",
     "time": "13:45", "status": "active"},
]
_next_alert_id = 2


def _now_hhmm():
    return datetime.now().strftime("%H:%M")


# ---------------------------------------------------------------------------
# REST — /devices  (contrat attendu par src/services/devices.js)
# ---------------------------------------------------------------------------
@app.get("/devices")
def get_devices():
    return devices


@app.get("/devices/{device_id}")
def get_device(device_id: str):
    device = next((d for d in devices if d["id"] == device_id), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.put("/devices/{device_id}")
def update_device(device_id: str, data: dict):
    device = next((d for d in devices if d["id"] == device_id), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.update(data)
    return device


@app.delete("/devices/{device_id}")
def delete_device(device_id: str):
    global devices
    before = len(devices)
    devices = [d for d in devices if d["id"] != device_id]
    if len(devices) == before:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"success": True}


# ---------------------------------------------------------------------------
# REST — /alerts  (contrat pour brancher Alerts.jsx quand vous serez prets)
# ---------------------------------------------------------------------------
@app.get("/alerts")
def get_alerts():
    return alerts


@app.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    alert = next((a for a in alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert["status"] = "resolved"
    return alert


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
# WebSocket (Socket.IO) — evenements attendus par src/services/websocket.js
# ---------------------------------------------------------------------------
@sio.event
async def connect(sid, environ):
    print(f"[ws] client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"[ws] client disconnected: {sid}")


@sio.on("device:connect")
async def on_device_connect(sid, data):
    print(f"[ws] device:connect from {sid}: {data}")


async def simulate_and_broadcast():
    """Boucle de fond : fait vivre les capteurs et pousse device:data / device:alert."""
    global _next_alert_id
    while True:
        await asyncio.sleep(5)
        for d in devices:
            if d["status"] == "offline":
                continue
            d["waterTemp"] = round(max(20, min(32, (d["waterTemp"] or 27) + random.uniform(-0.5, 0.5))), 1)
            d["windSpeed"] = round(max(0, (d["windSpeed"] or 10) + random.uniform(-2, 2)), 1)
            if random.random() < 0.3:
                d["catches"] = (d["catches"] or 0) + random.randint(0, 3)

            # declenche une alerte si le seuil de temperature est depasse
            if d["waterTemp"] and d["waterTemp"] > d["threshold"] and d["status"] != "alert":
                d["status"] = "alert"
                alert = {
                    "id": _next_alert_id,
                    "device": d["name"],
                    "type": "Temperature",
                    "message": f"Seuil depasse : {d['waterTemp']}C > {d['threshold']}C",
                    "time": _now_hhmm(),
                    "status": "active",
                }
                alerts.append(alert)
                _next_alert_id += 1
                await sio.emit("device:alert", alert)
                await sio.emit("device:status", {"id": d["id"], "status": "alert"})

        await sio.emit("device:data", {"devices": devices, "timestamp": _now_hhmm()})


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_and_broadcast())


app = socket_app