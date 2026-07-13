"""
Logique métier pour les bateaux. Les routers appellent ces fonctions,
ils ne parlent jamais directement à Mongo/Influx/Redis eux-mêmes.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from db import db, influx_query_api, INFLUX_BUCKET, INFLUX_ORG
from cache_aside import get_or_set, invalidate
from app.services import pecheurs_service


async def lister_bateaux(statut: Optional[str] = None) -> list[dict]:
    filtre = {}
    if statut:
        filtre["statut"] = statut
    curseur = db.bateaux.find(filtre)
    bateaux = await curseur.to_list(length=500)
    for b in bateaux:
        b["_id"] = str(b["_id"])
    return bateaux


async def obtenir_bateau(id_bateau: str) -> Optional[dict]:
    try:
        object_id = ObjectId(id_bateau)
    except InvalidId:
        return None

    bateau = await db.bateaux.find_one({"_id": object_id})
    if bateau:
        bateau["_id"] = str(bateau["_id"])
    return bateau


async def creer_bateau(data: dict) -> dict:
    data["statut"] = "actif"
    data["date_creation"] = datetime.now(timezone.utc)
    data["derniere_zone_connue"] = None
    resultat = await db.bateaux.insert_one(data)
    data["_id"] = str(resultat.inserted_id)

    await pecheurs_service.ajouter_bateau_au_pecheur(data["id_pecheur_proprietaire"], data["_id"])

    return data


async def modifier_bateau(id_bateau: str, updates: dict) -> Optional[dict]:
    updates_sans_none = {k: v for k, v in updates.items() if v is not None}
    if not updates_sans_none:
        return await obtenir_bateau(id_bateau)

    try:
        object_id = ObjectId(id_bateau)
    except InvalidId:
        return None

    await db.bateaux.update_one({"_id": object_id}, {"$set": updates_sans_none})
    invalidate(f"bateau:{id_bateau}:profil")  # le profil en cache est périmé
    return await obtenir_bateau(id_bateau)


def _lire_derniere_position_influx(id_bateau: str) -> Optional[dict]:
    """Va chercher le dernier point GPS connu dans InfluxDB (appelée seulement en cas de cache miss)."""
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -24h)
      |> filter(fn: (r) => r._measurement == "gps")
      |> filter(fn: (r) => r.id_bateau == "{id_bateau}")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 1)
    '''
    tables = influx_query_api.query(query, org=INFLUX_ORG)

    valeurs = {}
    horodatage = None
    for table in tables:
        for record in table.records:
            valeurs[record.get_field()] = record.get_value()
            horodatage = record.get_time()

    if not valeurs:
        return None

    return {
        "id_bateau": id_bateau,
        "lat": valeurs.get("lat"),
        "lng": valeurs.get("lng"),
        "vitesse": valeurs.get("vitesse"),
        "horodatage": horodatage.isoformat() if horodatage else None,
    }


def obtenir_derniere_position(id_bateau: str) -> Optional[dict]:
    """Cache-aside : Redis d'abord (TTL 90s), sinon InfluxDB."""
    return get_or_set(
        key=f"bateau:{id_bateau}:derniere_position",
        fetch_fn=lambda: _lire_derniere_position_influx(id_bateau),
        ttl=90,
    )