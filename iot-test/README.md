# Sandbox de test — Mosquitto + Node-RED

But : prouver que le pipeline complet fonctionne
(capteur → MQTT → Node-RED → ton API → MongoDB → Redis Pub/Sub → WebSocket),
sans dépendre du travail de Touré (broker sécurisé final) ni de Kouaho (vrais flows).

⚠️ Configuration volontairement basique (pas de TLS, pas d'auth MQTT) —
uniquement pour tester le principe capteurs + Node-RED, pas la version
finale sécurisée du projet (qui est gérée par Touré séparément).

---

## 1. Vérifier le nom exact de ton réseau Docker

```powershell
docker network ls
```
Note le nom exact (ex: `api_smart_fishing_net`). Si différent de celui dans
`docker-compose.iot-test.yml`, corrige la ligne `name:` du fichier.

## 2. Lancer le sandbox

```powershell
cd iot-test
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.iot-test.yml ps
```
Tu dois voir `iot_mosquitto` et `iot_node_red` en `running`.

## 3. Ouvrir l'éditeur Node-RED

Dans le navigateur : `http://localhost:1880`

## 4. Créer le compte technique pour Node-RED (une seule fois)

Les capteurs autres que GPS et SOS passent par des endpoints protégés — il
faut un compte pour que Node-RED puisse s'authentifier :

```powershell
docker exec -it sf_tools python -c "
import asyncio
from app.services import auth_service
asyncio.get_event_loop().run_until_complete(
    auth_service.creer_utilisateur('noderd_system', 'MOT_DE_PASSE_A_CHANGER', 'admin')
)
"
```



## 5. Importer le flow complet (7 capteurs)

1. Menu (☰) → **Import**
2. Colle le contenu de `flows_complet.json`
3. **Avant de déployer**, ouvre le nœud `Construire la requête de login` (double-clic)
   et remplace `CHANGE_MOI` par le vrai mot de passe créé à l'étape 4
4. Clique **Deploy**

Le nœud `Connexion (au démarrage + toutes les 50 min)` se déclenche automatiquement
1 seconde après le déploiement, récupère un token, et le stocke dans le contexte
global (`api_token`) — réutilisé par tous les capteurs protégés. Vérifie dans
le panneau de débogage que tu vois `token à jour` en vert sous ce nœud.

## 6. Envoyer des messages de test sur le broker

**Option A — un seul message manuel :**
```powershell
docker exec -it iot_mosquitto mosquitto_pub -h localhost -t "fishing/boat/<id_bateau_existant>/sos" -m "{\"lat\": 5.30, \"lng\": -4.05}"
```

**Option B — simuler les 7 capteurs en continu** (`simulate_capteurs_mqtt.py`) :
```powershell
docker exec -it sf_tools pip install -r requirements-dev.txt
docker exec -it sf_tools python iot-test/simulate_capteurs_mqtt.py <id_bateau_existant> --vitesse 60
```
Ce script publie sur MQTT (pas d'appel direct à l'API) — il joue vraiment le
rôle du capteur physique.

`--proba-sos 0.01` (1% par défaut, vérifié toutes les 30s réelles/accélérées)
contrôle la fréquence des déclenchements SOS aléatoires — augmente-la pour
une démo si tu veux en voir plus souvent.

## 7. Vérifier que ça a marché, à 3 niveaux

**a) Dans les panneaux de débogage de Node-RED** (à droite) : un panneau par
capteur, chacun affiche la réponse JSON de l'API. Pour l'inclinaison,
regarde le champ `alerte_sos_creee` — non nul quand `risque_chavirement: true`.

**b) Côté API (Swagger)** : `GET /bateaux/{id}/position`, `GET /alertes-sos`,
`GET /captures`, `GET /telemetrie/{id}/vent`, etc.

**c) En temps réel via le WebSocket** (si `test_websocket.py` tourne dans un
autre terminal) : les alertes SOS (manuelles ou automatiques) doivent
apparaître quasi instantanément.

---

## Arrêter le sandbox

```powershell
docker compose -f docker-compose.yml down
```
