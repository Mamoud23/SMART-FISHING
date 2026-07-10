# 🎣 SMART FISHING

## Suivi des pêches artisanales et sécurité des pêcheurs en Côte d'Ivoire

---

## 📌 Description

Smart Fishing est une infrastructure IoT sécurisée pour le suivi en temps réel des bateaux de pêche artisanale en Côte d'Ivoire.

**Objectif :** Sécuriser les communications MQTT entre les capteurs (bateaux) et le broker, et simuler des attaques pour valider les contre-mesures.

---

## 👥 Équipe

| Rôle | Profil | Responsabilités |
|------|--------|-----------------|
| Chef de projet & Sécurité | TOURE ALPHA MAMOUD | Architecture, broker HA, TLS, attaques, Nginx |
| Sécurité & Réseaux | DIBI KOUASSI JEAN-MARC | Tests intrusion, IDS/IPS, captures réseau |
| Backend & BD | DEMBELE YACOUBA | API FastAPI, InfluxDB, MongoDB, Redis |
| Frontend & Observabilité | KOUAHO AKOBE FREJUS | Dashboard React, Grafana, ELK |

---

## 🏗️ Architecture
CAPTEURS → BROKER → NODE-RED → NGINX → API → BASES DE DONNÉES → DASHBOARD

text

**Composants :**
- **Capteurs** : 7 capteurs (GPS, température, vent, captures, SOS, turbidité, inclinaison)
- **Broker** : Mosquitto (port 8883, TLS 1.2)
- **API** : FastAPI (3 instances)
- **Cache** : Redis Sentinel (3 nœuds)
- **Base de données** : InfluxDB + MongoDB
- **Frontend** : Dashboard React (6 vues)
- **Observabilité** : Grafana + Prometheus + ELK

---

## 📡 Capteurs (7)

| # | Capteur | Données | Topic MQTT |
|---|---------|---------|------------|
| 1 | GPS | Position, vitesse | `fishing/boat/+/gps` |
| 2 | Température eau | T° surface | `fishing/boat/+/water_temp` |
| 3 | Vent | Vitesse, direction | `fishing/boat/+/wind` |
| 4 | Captures | Espèce, poids, quantité | `fishing/boat/+/catch` |
| 5 | SOS | Alerte d'urgence | `fishing/boat/+/sos` |
| 6 | Turbidité | Clarté de l'eau | `fishing/boat/+/turbidity` |
| 7 | Inclinaison | Détection chavirement | `fishing/boat/+/tilt` |

---

## 🔐 Sécurité (TOURE ALPHA MAMOUD)

### Broker MQTT
- **Vulnérable** : port 1883, accès anonyme (pour attaques)
- **Sécurisé** : port 8883, TLS 1.2, authentification

### Certificats TLS
- CA + certificat serveur générés avec OpenSSL
- `openssl verify` → `server.crt: OK`

### Authentification
| Utilisateur | Rôle | Mot de passe |
|-------------|------|--------------|
| `capteur_temp` | Capteur IoT | `Smart-Fishing` |
| `superviseur` | Superviseur | `Smart-Fishing` |
| `tiers` | Test | `Smart-Fishing` |

### Nginx Load Balancer
- Répartition de charge entre 3 instances API
- `curl http://localhost/health` → `OK`

---

## ⚔️ Attaques simulées

| # | Attaque | Script | Statut |
|---|---------|--------|--------|
| 1 | Sniffing | `attack/sniffing.py` | ✅ |
| 2 | Spoofing | `attack/spoofing.py` | ✅ |
| 3 | Replay | `attack/replay.py` | ✅ |
| 4 | MITM | `attack/mitm.py` | ✅ |

---

## 🚀 Compilation
Builder et lancer toute la stack
docker compose up --build

Vérifier les réponse
docker compose ps

logger les services
docker compose logs -f api        # logs d'un service précis
docker compose logs -f dashboard

Arreter toute la stack
docker compose down -v

## 🚀 Installation

```bash
# Cloner le projet
git clone https://github.com/Mamoud23/SMART-FISHING.git
cd SMART-FISHING

# Installer les dépendances
sudo apt update
sudo apt install -y mosquitto mosquitto-clients python3 python3-pip nginx
pip3 install paho-mqtt scapy requests

# Lancer le broker sécurisé
sudo mosquitto -c broker/mosquitto_tls.conf -v

# Tester la connexion
mosquitto_sub -h localhost -p 8883 -t "#" -v --cafile /etc/mosquitto/ca.crt -u superviseur -P "Smart-Fishing"
