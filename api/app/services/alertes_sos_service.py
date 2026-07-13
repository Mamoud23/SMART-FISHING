"""
Logique métier pour les alertes SOS.

Point critique : chaque nouvelle alerte est publiée sur le canal Redis Pub/Sub
"sos:alertes", pour qu'un futur relai temps réel (WebSocket/SSE côté FastAPI,
consommé par le dashboard React) puisse la pousser immédiatement, sans polling.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from db import db
from cache_aside import publish_sos_alert, invalidate

from fastapi.encoders import jsonable_encoder 


async def creer_alerte(id_bateau: str, gps: dict) -> dict:
    document = {
        "id_bateau": id_bateau,
        "horodatage": datetime.now(timezone.utc),
        "gps": gps,
        "statut": "ouverte",
        "resolue_par": None,
        "date_resolution": None,
    }
    resultat = await db.alertes_sos.insert_one(document)
    document["_id"] = str(resultat.inserted_id)

    # Envoie une version sérialisable (avec la date convertie en string) au Pub/Sub
    publish_sos_alert(jsonable_encoder(document))
    
    invalidate("sos:nb_ouvertes")

    return document


async def lister_alertes(statut: Optional[str] = None) -> list[dict]:
    filtre = {}
    if statut:
        filtre["statut"] = statut
    curseur = db.alertes_sos.find(filtre).sort("horodatage", -1)
    alertes = await curseur.to_list(length=500)
    for a in alertes:
        a["_id"] = str(a["_id"])
    return alertes


async def obtenir_alerte(id_alerte: str) -> Optional[dict]:
    try:
        object_id = ObjectId(id_alerte)
    except InvalidId:
        return None

    alerte = await db.alertes_sos.find_one({"_id": object_id})
    if alerte:
        alerte["_id"] = str(alerte["_id"])
    return alerte


async def _changer_statut(id_alerte: str, nouveau_statut: str, resolue_par: Optional[str] = None) -> Optional[dict]:
    try:
        object_id = ObjectId(id_alerte)
    except InvalidId:
        return None

    updates = {"statut": nouveau_statut}
    if nouveau_statut == "resolue":
        updates["date_resolution"] = datetime.now(timezone.utc)
        updates["resolue_par"] = resolue_par

    resultat = await db.alertes_sos.update_one({"_id": object_id}, {"$set": updates})
    if resultat.matched_count == 0:
        return None

    invalidate("sos:nb_ouvertes")
    return await obtenir_alerte(id_alerte)


async def prendre_en_charge(id_alerte: str) -> Optional[dict]:
    return await _changer_statut(id_alerte, "prise_en_charge")


async def resoudre(id_alerte: str, resolue_par: Optional[str] = None) -> Optional[dict]:
    return await _changer_statut(id_alerte, "resolue", resolue_par=resolue_par)


async def _compter_ouvertes_mongo() -> int:
    return await db.alertes_sos.count_documents({"statut": "ouverte"})


async def compter_alertes_ouvertes() -> dict:
    """
    Cache-aside manuel (et non via get_or_set) car ici le fetch (Mongo) est
    asynchrone, alors que get_or_set()/cache_aside.py est écrit pour un fetch
    synchrone. TTL volontairement très court (5s) : c'est une donnée temps réel
    critique, mieux vaut un cache qui expire vite qu'une invalidation complexe.
    """
    from redis_client import get_redis_replica, get_redis_master
    import json

    cle = "sos:nb_ouvertes"
    try:
        cache = get_redis_replica().get(cle)
        if cache is not None:
            return json.loads(cache)
    except Exception as e:
        print(f"[cache-aside] Lecture Redis indisponible ({e}), on lit directement Mongo.")

    nb = await _compter_ouvertes_mongo()
    resultat = {"nb_ouvertes": nb}

    try:
        get_redis_master().set(cle, json.dumps(resultat), ex=5)
    except Exception as e:
        print(f"[cache-aside] Écriture Redis indisponible ({e}).")

    return resultat