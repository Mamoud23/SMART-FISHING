#!/bin/bash
# Génération des certificats TLS pour SMART-FISHING

echo "🔐 Génération des certificats TLS..."

# 1. CA (Certificate Authority)
echo "📜 Génération de la CA..."
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt -subj "/CN=SMART-FISHING CA"

# 2. Certificat serveur
echo "📜 Génération du certificat serveur..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=localhost"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# 3. Vérification
echo "✅ Vérification de la chaîne de confiance..."
openssl verify -CAfile ca.crt server.crt

echo "✅ Certificats générés avec succès !"
ls -la
