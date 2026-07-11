"""
Connexion Redis via Sentinel : ne cible JAMAIS "redis-master" directement,
mais interroge les sentinels pour savoir qui est le master actuel.
Cela permet de survivre à un failover automatique sans changer le code.
"""

import os
from redis.sentinel import Sentinel

SENTINEL_HOSTS = [
    (os.environ.get("REDIS_SENTINEL_1", "sentinel1"), 26379),
    (os.environ.get("REDIS_SENTINEL_2", "sentinel2"), 26379),
    (os.environ.get("REDIS_SENTINEL_3", "sentinel3"), 26379),
]
MASTER_NAME = os.environ.get("REDIS_MASTER_NAME", "mymaster")

sentinel = Sentinel(SENTINEL_HOSTS, socket_timeout=0.5)


def get_redis_master():
    """Connexion en écriture : toujours vers le master actuel (découvert via Sentinel)."""
    return sentinel.master_for(MASTER_NAME, socket_timeout=0.5, decode_responses=True)


def get_redis_replica():
    """Connexion en lecture : peut être répartie sur les replicas (charge en lecture)."""
    return sentinel.slave_for(MASTER_NAME, socket_timeout=0.5, decode_responses=True)


def get_current_master_address():
    """
    Utile pour debug/démo : affiche qui est le master actuel selon les sentinels.
    Pendant la fenêtre de failover (quelques secondes après la panne du master),
    il est normal qu'aucun master ne soit trouvable un court instant : on retourne
    None plutôt que de laisser planter l'appelant.
    """
    try:
        return sentinel.discover_master(MASTER_NAME)
    except Exception:
        return None