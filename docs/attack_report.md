# Rapport d'Attaque — SMART FISHING

## Suivi des pêches artisanales et sécurité des pêcheurs en Côte d'Ivoire

---

## 1. Introduction

Ce rapport documente les 4 attaques réseau simulées sur l'infrastructure Smart Fishing. L'objectif est de prouver les vulnérabilités du système sans sécurité, puis de valider l'efficacité des contre-mesures (TLS, authentification, ACL).

---

## 2. Environnement de test

| Composant | Détail |
|-----------|--------|
| Broker | Mosquitto 2.0.11 |
| Port vulnérable | 1883 (accès anonyme, pas de TLS) |
| Port sécurisé | 8883 (TLS 1.2, authentification) |
| Système | Ubuntu 22.04 (WSL2) |
| Langage | Python 3 (paho-mqtt) |

---

## 3. Attaque 1 — Sniffing (interception passive)

### Description

Le sniffing consiste à écouter passivement le trafic réseau pour intercepter les données transmises, sans interaction avec les parties légitimes.
Le script se connecte au broker vulnérable (port 1883) et s'abonne à l'ensemble des topics (#), affichant en clair chaque message intercepté.


mv "Attaque_Sniffing.png" sniffing.png


⚠️ Vulnérabilité exploitée : Absence de chiffrement du canal de transport (pas de TLS sur le port 1883). Toute donnée capteur (position GPS, température, inclinaison, captures) est lisible en clair par quiconque peut observer le trafic réseau, sans avoir besoin d'identifiants ni de casser un quelconque mécanisme de sécurité.



### 4. Attaque 2 — Spoofing (usurpation de capteur)
Description
Le spoofing consiste à se faire passer pour un capteur légitime et à publier de fausses données directement sur un topic existant, sans avoir besoin d'intercepter le moindre trafic réel.


### 4.1 Spoofing du capteur de température

bash
python3 spoofing.py



Le script se connecte au broker avec un Client ID usurpé (capteur_TEMP_001) et publie 5 messages de température anormale (40–45°C) avec une alerte critique, sans qu'aucune vérification d'identité ne soit requise par le broker.
