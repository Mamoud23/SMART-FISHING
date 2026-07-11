"""
Logique métier pour les captures (capteur 4 du document de justification).

Mode événementiel, stocké dans MongoDB (pas InfluxDB) car les champs sont
variables (espèce en texte) et les requêtes utiles sont des agrégations
(totaux par espèce/bateau/période) plutôt que des séries temporelles brutes.

Enjeu sécurité IoT rappelé dans le document : la falsification de ces données
peut corrompre les statistiques nationales (MIRAH) et fausser les quotas de
pêche — d'où l'intérêt d'une validation stricte au niveau des schémas Pydantic
(déjà faite dans app/models/capture.py) avant toute écriture ici.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from db import db


async def creer_capture(data: dict) -> dict:
    document = {
        "id_bateau": data["id_bateau"],
        "espece": data["espece"],
        "poids_kg": data["poids_kg"],
        "quantite": data["quantite"],
        "gps_a_la_capture": data["gps_a_la_capture"],
        "horodatage": data.get("horodatage") or datetime.now(timezone.utc),
    }
    resultat = await db.captures.insert_one(document)
    document["_id"] = str(resultat.inserted_id)
    return document


async def obtenir_capture(id_capture: str) -> Optional[dict]:
    try:
        object_id = ObjectId(id_capture)
    except InvalidId:
        return None

    capture = await db.captures.find_one({"_id": object_id})
    if capture:
        capture["_id"] = str(capture["_id"])
    return capture


async def lister_captures(
    id_bateau: Optional[str] = None,
    depuis: Optional[datetime] = None,
    jusqu_a: Optional[datetime] = None,
) -> list[dict]:
    filtre = {}
    if id_bateau:
        filtre["id_bateau"] = id_bateau
    if depuis or jusqu_a:
        filtre["horodatage"] = {}
        if depuis:
            filtre["horodatage"]["$gte"] = depuis
        if jusqu_a:
            filtre["horodatage"]["$lte"] = jusqu_a

    curseur = db.captures.find(filtre).sort("horodatage", -1)
    captures = await curseur.to_list(length=1000)
    for c in captures:
        c["_id"] = str(c["_id"])
    return captures


async def statistiques_par_espece(
    id_bateau: Optional[str] = None,
    depuis: Optional[datetime] = None,
    jusqu_a: Optional[datetime] = None,
) -> list[dict]:
    """Agrégation Mongo : totaux par espèce (poids, quantité, nombre de captures)."""
    filtre = {}
    if id_bateau:
        filtre["id_bateau"] = id_bateau
    if depuis or jusqu_a:
        filtre["horodatage"] = {}
        if depuis:
            filtre["horodatage"]["$gte"] = depuis
        if jusqu_a:
            filtre["horodatage"]["$lte"] = jusqu_a

    pipeline = []
    if filtre:
        pipeline.append({"$match": filtre})

    pipeline += [
        {
            "$group": {
                "_id": "$espece",
                "poids_total_kg": {"$sum": "$poids_kg"},
                "quantite_totale": {"$sum": "$quantite"},
                "nombre_captures": {"$sum": 1},
            }
        },
        {"$sort": {"poids_total_kg": -1}},
    ]

    curseur = db.captures.aggregate(pipeline)
    resultats = await curseur.to_list(length=200)

    return [
        {
            "espece": r["_id"],
            "poids_total_kg": r["poids_total_kg"],
            "quantite_totale": r["quantite_totale"],
            "nombre_captures": r["nombre_captures"],
        }
        for r in resultats
    ]