"""
Modules de connexion à réutiliser dans le backend FastAPI.
Charge les paramètres depuis les variables d'environnement (.env).
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# ---------- MongoDB (asynchrone, pour FastAPI) ----------

MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "smart_fishing")

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]

# Exemple d'utilisation dans un endpoint FastAPI :
#   from db import db
#   bateau = await db.bateaux.find_one({"_id": id_bateau})


# ---------- InfluxDB ----------

INFLUX_URL = os.environ["INFLUX_URL"]
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
INFLUX_ORG = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "telemetrie_peche")

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
influx_query_api = influx_client.query_api()

# Exemple d'écriture :
#   from influxdb_client import Point
#   point = Point("gps").tag("id_bateau", "bateau_0007").field("lat", 5.32).field("lng", -4.01)
#   influx_write_api.write(bucket=INFLUX_BUCKET, record=point)

# Exemple de lecture (Flux) :
#   query = f'from(bucket:"{INFLUX_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "gps")'
#   tables = influx_query_api.query(query)