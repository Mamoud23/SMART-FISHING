"""
Initialise le replica set MongoDB (rs0) à partir de Python.
À exécuter UNE SEULE FOIS, juste après le démarrage des 3 conteneurs.

Utilisation :
    python init_replica_set.py
"""

from pymongo import MongoClient
import time

ADMIN_USER = "admin"
ADMIN_PASSWORD = "bdgl2026"

# On se connecte à mongo1 directement (pas encore de replica set actif)
client = MongoClient(
    "mongodb://mongo1:27017/",
    username=ADMIN_USER,
    password=ADMIN_PASSWORD,
    authSource="admin",
    directConnection=True,
)

config = {
    "_id": "rs0",
    "members": [
        {"_id": 0, "host": "mongo1:27017"},
        {"_id": 1, "host": "mongo2:27017"},
        {"_id": 2, "host": "mongo3:27017"},
    ],
}

print("Initialisation du replica set...")
client.admin.command("replSetInitiate", config)

print("Attente de l'élection du primaire...")
time.sleep(10)

status = client.admin.command("replSetGetStatus")
for member in status["members"]:
    print(f"  {member['name']} -> {member['stateStr']}")

print("Replica set initialisé.")