"""
Logique métier pour les pêcheurs. CRUD simple, moins critique que les autres
ressources (pas de télémétrie, pas de cache Redis nécessaire ici).
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from db import db


async def lister_pecheurs() -> list[dict]:
    curseur = db.pecheurs.find({})
    pecheurs = await curseur.to_list(length=500)
    for p in pecheurs:
        p["_id"] = str(p["_id"])
    return pecheurs


async def obtenir_pecheur(id_pecheur: str) -> Optional[dict]:
    try:
        object_id = ObjectId(id_pecheur)
    except InvalidId:
        return None

    pecheur = await db.pecheurs.find_one({"_id": object_id})
    if pecheur:
        pecheur["_id"] = str(pecheur["_id"])
    return pecheur


async def creer_pecheur(data: dict) -> dict:
    data["bateaux"] = []
    data["date_creation"] = datetime.now(timezone.utc)

    try:
        resultat = await db.pecheurs.insert_one(data)
    except DuplicateKeyError:
        raise ValueError(f"Le numéro de licence '{data['numero_licence']}' est déjà utilisé.")

    data["_id"] = str(resultat.inserted_id)
    return data


async def modifier_pecheur(id_pecheur: str, updates: dict) -> Optional[dict]:
    updates_sans_none = {k: v for k, v in updates.items() if v is not None}
    if not updates_sans_none:
        return await obtenir_pecheur(id_pecheur)

    try:
        object_id = ObjectId(id_pecheur)
    except InvalidId:
        return None

    await db.pecheurs.update_one({"_id": object_id}, {"$set": updates_sans_none})
    return await obtenir_pecheur(id_pecheur)


async def ajouter_bateau_au_pecheur(id_pecheur: str, id_bateau: str) -> Optional[dict]:
    """Appelée par bateaux_service.creer_bateau pour maintenir la liste bateaux[] à jour."""
    try:
        object_id = ObjectId(id_pecheur)
    except InvalidId:
        return None

    await db.pecheurs.update_one({"_id": object_id}, {"$addToSet": {"bateaux": id_bateau}})
    return await obtenir_pecheur(id_pecheur)