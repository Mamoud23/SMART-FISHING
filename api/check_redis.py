"""
Vérifie l'état du cluster Redis Sentinel : qui est master, combien de replicas,
et teste une écriture/lecture simple.

Utilisation :
    docker exec -it sf_tools python check_redis.py
"""

from redis_client import get_redis_master, get_redis_replica, get_current_master_address

print("Master actuel (découvert via Sentinel) :", get_current_master_address())

master = get_redis_master()
master.set("test:ping", "pong", ex=30)
print("Écriture sur le master : OK")

replica = get_redis_replica()
import time
time.sleep(0.3)  # laisser le temps à la réplication
valeur = replica.get("test:ping")
print("Lecture depuis un replica :", valeur)

if valeur == "pong":
    print("\nLe cluster Redis Sentinel fonctionne correctement.")
else:
    print("\nATTENTION : la réplication ne semble pas encore synchronisée, réessaie dans quelques secondes.")