from datetime import datetime, timezone
from typing import Optional

from pymongo.errors import DuplicateKeyError

from db import db
from app.core.security import hasher_mot_de_passe, verifier_mot_de_passe


async def creer_utilisateur(username: str, password: str, role: str, id_pecheur: Optional[str] = None) -> dict:
    document = {
        "username": username,
        "password_hash": hasher_mot_de_passe(password),
        "role": role,
        "id_pecheur": id_pecheur,
        "date_creation": datetime.now(timezone.utc),
    }
    try:
        resultat = await db.utilisateurs.insert_one(document)
    except DuplicateKeyError:
        raise ValueError(f"Le nom d'utilisateur '{username}' est déjà pris.")

    document["_id"] = str(resultat.inserted_id)
    return document


async def obtenir_utilisateur(username: str) -> Optional[dict]:
    return await db.utilisateurs.find_one({"username": username})


async def authentifier(username: str, password: str) -> Optional[dict]:
    utilisateur = await obtenir_utilisateur(username)
    if not utilisateur:
        return None
    if not verifier_mot_de_passe(password, utilisateur["password_hash"]):
        return None
    return utilisateur