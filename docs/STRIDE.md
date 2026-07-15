# Analyse STRIDE — SMART FISHING

## 1. Introduction

L'analyse STRIDE permet d'identifier les menaces pesant sur chaque composant de l'infrastructure Smart Fishing.

## 2. Matrice STRIDE

| Composant | Spoofing | Tampering | Repudiation | Information Disclosure | DoS | Elevation |
|-----------|----------|-----------|-------------|----------------------|-----|-----------|
| **Broker MQTT** | 🔴 Élevé | 🔴 Élevé | 🟡 Moyen | 🔴 Élevé | 🟡 Moyen | 🔴 Élevé |
| **API FastAPI** | 🔴 Élevé | 🔴 Élevé | 🟡 Moyen | 🔴 Élevé | 🟡 Moyen | 🔴 Élevé |
| **Capteurs** | 🔴 Élevé | 🟡 Moyen | 🟢 Faible | 🟡 Moyen | 🟢 Faible | 🟢 Faible |
| **Dashboard** | 🟡 Moyen | 🟢 Faible | 🟢 Faible | 🟡 Moyen | 🟢 Faible | 🟡 Moyen |
| **Base de données** | 🟢 Faible | 🟡 Moyen | 🟢 Faible | 🔴 Élevé | 🟢 Faible | 🟢 Faible |

## 3. Détail des menaces

| Menace STRIDE | Explication | Attaque associée |
|---------------|-------------|------------------|
| **Spoofing** | Un attaquant peut usurper l'identité d'un capteur pour publier de fausses données | Attaque 2 — Spoofing |
| **Tampering** | Un attaquant peut modifier les données en transit | Attaque 4 — MITM |
| **Repudiation** | Les actions ne sont pas traçables (absence de logs) | - |
| **Information Disclosure** | Les données sont visibles en clair | Attaque 1 — Sniffing |
| **Denial of Service** | Un attaquant peut saturer le broker avec des messages | Attaque 3 — Replay |
| **Elevation of Privilege** | Un attaquant peut se connecter avec des identifiants volés | - |

## 4. Contre-mesures STRIDE

| Menace | Contre-mesure | Statut |
|--------|---------------|--------|
| Spoofing | Authentification + ACL | ✅ Appliqué |
| Tampering | TLS + mTLS | ✅ Appliqué |
| Repudiation | Logs centralisés | ⏳ À implémenter |
| Information Disclosure | TLS (port 8883) | ✅ Appliqué |
| DoS | Rate limiting + Redis | ⏳ À implémenter |
| Elevation | Authentification forte | ✅ Appliqué |
