"""
À exécuter UNE SEULE FOIS : crée l'index unique sur "username" et un premier
compte admin. Sans ce script, impossible de créer d'autres comptes admin/autorite
(POST /auth/register-privilegie exige déjà d'être admin -> problème de l'oeuf et
de la poule pour le tout premier compte).

Utilisation :
    docker exec -it sf_tools python bootstrap_admin.py <username> <password>
"""

import sys
import asyncio

from pymongo import MongoClient
from passlib.context import CryptContext
from datetime import datetime, timezone
import os

if len(sys.argv) < 3:
    print("Usage : python bootstrap_admin.py <username> <password>")
    sys.exit(1)

username, password = sys.argv[1], sys.argv[2]

MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "smart_fishing")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

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