import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Récupérer l'URI magique
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Initialiser le client PyMongo (il gère le Replica Set et l'auth tout seul grâce à l'URI)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Exemple : insérer une donnée pour tester (ça créera la base "smart_fishing" automatiquement !)
try:
    db.telemetrie.insert_one({"statut": "test_connexion", "projet": "Smart Fishing"})
    print("Succès ! Connexion établie et données insérées.")
except Exception as e:
    print(f"Erreur de connexion : {e}")