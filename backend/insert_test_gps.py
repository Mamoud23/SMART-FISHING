"""
Insère un point GPS de test dans InfluxDB, pour un bateau donné.

Utilisation (depuis le conteneur sf_tools ou sf_api, car "influxdb" n'est
résoluble que dans le réseau Docker) :

    docker exec -it sf_tools python insert_test_gps.py <id_bateau>

Exemple :
    docker exec -it sf_tools python insert_test_gps.py 6874f2a1b8e4a1234567890a
"""

import sys
from datetime import datetime, timezone

from influxdb_client import Point

from db import influx_write_api, INFLUX_BUCKET, INFLUX_ORG

if len(sys.argv) < 2:
    print("Usage : python insert_test_gps.py <id_bateau>")
    print("(récupère l'id_bateau via GET /bateaux dans Swagger : http://localhost:8000/docs)")
    sys.exit(1)

id_bateau = sys.argv[1]

point = (
    Point("gps")
    .tag("id_bateau", id_bateau)
    .field("lat", 5.32)
    .field("lng", -4.01)
    .field("vitesse", 8.5)
    .time(datetime.now(timezone.utc))
)

influx_write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

print(f"Point GPS inséré pour le bateau '{id_bateau}'.")
print("Teste maintenant : GET /bateaux/{id_bateau}/position dans Swagger, ou :")
print(f'  docker exec -it sf_tools curl http://api:8000/bateaux/{id_bateau}/position')