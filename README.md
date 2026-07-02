# SMART-FISHING

# Suivi des pêches artisanales et sécurité des pêcheurs en Côte d'Ivoire

### Équipe
- **TOURE ALPHA MAMOUD** : Chef de projet & Sécurité (Architecture, broker HA, TLS, attaques)
- **DIBI KOUASSI JEAN-MARC** : Sécurité & Réseaux (Tests intrusion, IDS/IPS, captures réseau)
- **DEMBELE YACOUBA** : Backend & BD (API FastAPI, InfluxDB, MongoDB, Redis)
- **KOUAHO FREJUS** : Frontend & Observabilité (Dashboard React, Grafana, ELK)

### Capteurs (7)
1. GPS → Position, vitesse
2. Température eau → T° surface
3. Vent → Vitesse, direction
4. Captures → Espèce, poids, quantité
5. Bouton SOS → Alerte d'urgence
6. Turbidité → Clarté de l'eau
7. Inclinaison → Détection de chavirement

### Stack technique
- Broker : EMQX / Mosquitto HA + TLS 1.3
- Stockage : InfluxDB + MongoDB
- Cache : Redis Sentinel (3 nœuds)
- API : FastAPI (3 instances) + Nginx LB
- Frontend : React 18 + Leaflet + Recharts
- Observabilité : Grafana + Prometheus + ELK
- Déploiement : Docker Compose


Mini-Projet Sécurité IoT : Suivi des pêches artisanales et sécurité des pêcheurs en Côte d'Ivoire
