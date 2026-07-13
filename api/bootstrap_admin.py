"""
À exécuter UNE SEULE FOIS : crée le tout premier compte admin.
Sans ce script, impossible de créer d'autres comptes admin/autorite
(POST /auth/register-privilegie exige déjà d'être admin).

Utilisation :
    docker exec -it sf_tools python bootstrap_admin.py <username> <password>
"""

import sys
from pymongo import MongoClient
from passlib.context import CryptContext
from datetime import datetime, timezone

if len(sys.argv) < 3:
    print("Usage : python bootstrap_admin.py <username> <password>")
    sys.exit(1)

username, password = sys.argv[1], sys.argv[2]

client = MongoClient("mongodb://mongo1:27017,mongo2:27017,mongo3:27017/", replicaSet="rs0")
db = client["smart_fishing"]

db.utilisateurs.create_index("username", unique=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    db.utilisateurs.insert_one({
        "username": username,
        "password_hash": pwd_context.hash(password),
        "role": "admin",
        "id_pecheur": None,
        "date_creation": datetime.now(timezone.utc),
    })
    print(f"Compte admin '{username}' créé avec succès.")
except Exception as e:
    print(f"Erreur (le compte existe peut-être déjà) : {e}")