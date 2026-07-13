"""
Crée la base smart_fishing, les collections et les index.
À exécuter UNE SEULE FOIS, juste après init_replica_set.py.

Utilisation :
    docker exec -it sf_tools python init_mongo.py
"""

from pymongo import MongoClient

DB_NAME = "smart_fishing"

client = MongoClient(
    "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/",
    replicaSet="rs0",
)

db = client[DB_NAME]

print("Création des collections...")
for collection in ["bateaux", "pecheurs", "captures", "alertes_sos", "utilisateurs"]:
    if collection not in db.list_collection_names():
        db.create_collection(collection)

print("Création des index...")
db.bateaux.create_index("id_pecheur_proprietaire")
db.bateaux.create_index("statut")

db.pecheurs.create_index("numero_licence", unique=True)

db.captures.create_index([("id_bateau", 1), ("horodatage", -1)])

db.alertes_sos.create_index([("statut", 1), ("horodatage", -1)])

db.utilisateurs.create_index("username", unique=True)

print("Initialisation MongoDB terminée : collections et index créés.")