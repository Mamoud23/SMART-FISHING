"""
Pattern cache-aside générique, à utiliser dans les endpoints FastAPI.

Exemple d'utilisation :

    from cache_aside import get_or_set, invalidate

    async def get_position_bateau(id_bateau: str):
        return get_or_set(
            key=f"bateau:{id_bateau}:derniere_position",
            fetch_fn=lambda: lire_derniere_position_influx(id_bateau),  # fonction qui va chercher en base si pas en cache
            ttl=90,
        )
"""

import json
from redis_client import get_redis_master, get_redis_replica


def get_or_set(key: str, fetch_fn, ttl: int = 60, use_replica_for_read: bool = True):
    """
    1. Essaie de lire depuis Redis (replica si possible, pour répartir la charge).
    2. Si absent (cache miss), appelle fetch_fn() pour aller chercher en base (Mongo/Influx).
    3. Écrit le résultat dans Redis (toujours sur le master) avec un TTL.
    4. Si Redis est indisponible (panne totale), on se rabat directement sur fetch_fn()
       -> dégradation gracieuse, l'API continue de fonctionner sans cache.
    """
    try:
        r_read = get_redis_replica() if use_replica_for_read else get_redis_master()
        cached = r_read.get(key)
        if cached is not None:
            return json.loads(cached)
    except Exception as e:
        print(f"[cache-aside] Lecture Redis indisponible ({e}), on lit directement la base.")

    value = fetch_fn()

    try:
        r_write = get_redis_master()
        r_write.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        print(f"[cache-aside] Écriture Redis indisponible ({e}), valeur non mise en cache.")

    return value


def invalidate(key: str):
    """À appeler après un PATCH/POST qui modifie une donnée mise en cache."""
    try:
        get_redis_master().delete(key)
    except Exception as e:
        print(f"[cache-aside] Impossible d'invalider la clé '{key}' ({e}).")


def publish_sos_alert(alerte: dict):
    """Publie une nouvelle alerte SOS sur le canal Pub/Sub, pour un futur relai temps réel (WebSocket/SSE)."""
    try:
        get_redis_master().publish("sos:alertes", json.dumps(alerte))
    except Exception as e:
        print(f"[cache-aside] Impossible de publier l'alerte SOS ({e}).")