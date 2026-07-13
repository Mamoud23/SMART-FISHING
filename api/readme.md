# Configuration MongoDB + InfluxDB — Smart Fishing (100% Python, via Docker)

Fichiers à mettre dans le même dossier :
`docker-compose.yml`, `.env`, `requirements.txt`, `init_replica_set.py`, `init_mongo.py`, `check_influx.py`, `db.py`.

⚠️ **Point important** : les scripts Python ne peuvent PAS être lancés depuis ton terminal Windows/Mac
directement (`python init_replica_set.py` échoue avec une erreur `getaddrinfo failed`).
En cause : les noms `mongo1`, `mongo2`, `influxdb`, etc. n'existent que **dans le réseau interne
de Docker**, pas sur ta machine.

La solution : un petit conteneur "outils" (`tools`) tourne sur le même réseau Docker que les bases,
et c'est LUI qui exécute les scripts. C'est pour ça qu'on ajoute ce service dans `docker-compose.yml`.

---

## Étape 1 — Générer la clé d'authentification interne MongoDB (une seule fois)

Sur Windows, utilise **Git Bash** (pas PowerShell) si tu as `openssl` :
```bash
openssl rand -base64 756 > mongo-keyfile
```

Sinon, en Python (marche partout, y compris PowerShell) :
```powershell
python -c "import secrets, base64; open('mongo-keyfile', 'wb').write(base64.b64encode(secrets.token_bytes(564)))"
```

## Étape 2 — Lancer tous les conteneurs (bases + outils)

```bash
docker compose up -d
docker compose ps
```

Tu dois voir `mongo1`, `mongo2`, `mongo3`, `influxdb`, `sf_tools` tous en état `running`/`Up`.

## Étape 3 — Installer les dépendances Python DANS le conteneur outils

```bash
docker exec -it sf_tools pip install -r requirements.txt
```

## Étape 4 — Initialiser le replica set MongoDB

```bash
docker exec -it sf_tools python init_replica_set.py
```

Tu dois voir un membre `PRIMARY` et deux `SECONDARY`.

## Étape 5 — Créer la base, l'utilisateur applicatif, les collections et les index

```bash
docker exec -it sf_tools python init_mongo.py
```

## Étape 6 — Vérifier InfluxDB

```bash
docker exec -it sf_tools python check_influx.py
```

Tu dois voir le bucket `telemetrie_peche` dans la liste.

---

## Étape 7 — Vérifier le cluster Redis Sentinel

```bash
docker exec -it sf_tools python check_redis.py
```

Ce script affiche le master actuel (découvert dynamiquement via les sentinels), écrit une valeur
de test, et vérifie qu'elle est bien répliquée sur un replica.

## Étape 8 — Démo de failover automatique (pour la soutenance)

1. Dans un premier terminal, observe le master actuel en continu :
```bash
docker exec -it sf_tools python -c "from redis_client import get_current_master_address; import time; [print(get_current_master_address()) or time.sleep(2) for _ in range(60)]"
```

2. Dans un second terminal, coupe le master en pleine démo :
```bash
docker stop redis-master
```

3. Observe dans le premier terminal : après quelques secondes (down-after-milliseconds = 5000ms),
   les sentinels détectent la panne, votent (quorum = 2/3), et promeuvent un replica en nouveau
   master. L'adresse affichée change automatiquement.

4. Relance l'ancien master (il rejoindra le cluster comme replica) :
```bash
docker start redis-master
```

Cette démo illustre concrètement la haute disponibilité demandée dans le cahier des charges,
sans aucune interruption de service côté client (le client Python redécouvre le master via Sentinel,
jamais via un nom fixe).

---

## Pourquoi cette approche (et pas depuis Windows directement) ?

Plus tard, ton API FastAPI tournera **elle aussi dans un conteneur Docker** (ajouté au même
`docker-compose.yml`, sur le même réseau `smart_fishing_net`). Elle pourra alors se connecter
directement à `mongo1`, `mongo2`, `mongo3`, `influxdb` sans aucun problème — exactement comme
le fait `sf_tools` maintenant. Tu utilises donc dès maintenant la bonne méthode de travail.

Si un jour tu veux vraiment lancer un script Python depuis Windows directement (hors Docker),
il faudrait remplacer les noms `mongo1`/`mongo2`/`mongo3`/`influxdb` par `localhost` et ajuster
les ports — mais ce n'est pas recommandé, ça complique inutilement les choses.

---

## Résumé des accès

| Service | Adresse (depuis un autre conteneur du même réseau) | Adresse (depuis Windows, ex. MongoDB Compass) | Identifiants |
|---|---|---|---|
| MongoDB | `mongo1:27017,mongo2:27017,mongo3:27017` | `localhost:27017` | `app_backend` / `app_backend_password_a_changer` |
| InfluxDB UI | `http://influxdb:8086` | `http://localhost:8086` | `admin` / `admin_password_a_changer` |
| Token Influx | — | — | `mon-token-admin-a-changer` |

⚠️ Avant la soutenance : change tous les mots de passe/tokens marqués `_a_changer`.

## Étape suivante

Les schémas Pydantic (bateaux, pêcheurs, captures, alertes SOS) et les premiers endpoints FastAPI,
qui viendront s'ajouter comme un nouveau service dans ce même `docker-compose.yml`.