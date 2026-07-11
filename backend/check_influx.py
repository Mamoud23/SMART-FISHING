"""
Vérifie que InfluxDB est bien initialisé et que le bucket existe.
À exécuter DANS le conteneur "tools" (voir README.md).

Utilisation :
    docker exec -it sf_tools python check_influx.py
"""

import os
from influxdb_client import InfluxDBClient

INFLUX_URL = os.environ["INFLUX_URL"]       # http://influxdb:8086
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
INFLUX_ORG = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "telemetrie_peche")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

buckets_api = client.buckets_api()
buckets = buckets_api.find_buckets().buckets

print("Buckets trouvés :")
for b in buckets:
    print(f"  - {b.name}")

if any(b.name == INFLUX_BUCKET for b in buckets):
    print(f"\nLe bucket '{INFLUX_BUCKET}' existe. InfluxDB est prêt.")
else:
    print(f"\nATTENTION : le bucket '{INFLUX_BUCKET}' n'existe pas.")

client.close()