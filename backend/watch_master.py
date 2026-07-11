"""
Observe en continu qui est le master Redis actuel (démo de failover Sentinel).
Contrairement à un appel direct en boucle, ce script survit à la courte fenêtre
d'indisponibilité pendant la bascule (affiche "(bascule en cours...)" au lieu de planter).

Utilisation :
    docker exec -it sf_tools python watch_master.py
"""

import time
from redis_client import get_current_master_address

print("Surveillance du master Redis (Ctrl+C pour arrêter)...\n")

dernier_master = None
for _ in range(120):
    master = get_current_master_address()
    if master is None:
        print("(bascule en cours...)")
    elif master != dernier_master:
        print(f">>> Master actuel : {master}")
        dernier_master = master
    else:
        print(f"Master actuel : {master}")
    time.sleep(2)