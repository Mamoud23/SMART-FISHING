"""
Configuration partagée pour tous les tests.

Principe : on ne touche JAMAIS aux vraies bases (Mongo/Influx/Redis) pendant
les tests. Chaque fixture remplace le client réel par un client en mémoire :
- MongoDB   -> mongomock-motor (même API que Motor, mais tout en RAM)
- Redis     -> fakeredis (même API que redis-py, tout en RAM)
- InfluxDB  -> MagicMock (pas d'équivalent "in-memory" officiel, donc on
              simule les réponses attendues directement dans chaque test)

Variables d'environnement fictives déclarées AVANT tout import de l'app,
sinon db.py / security.py plantent à l'import (os.environ["JWT_SECRET_KEY"]
par exemple).
"""

import os
import asyncio

os.environ.setdefault("MONGO_URI", "mongodb://fake-host:27017")
os.environ.setdefault("MONGO_DB_NAME", "smart_fishing_test")
os.environ.setdefault("INFLUX_URL", "http://fake-host:8086")
os.environ.setdefault("INFLUX_TOKEN", "fake-token")
os.environ.setdefault("INFLUX_ORG", "smart_fishing")
os.environ.setdefault("INFLUX_BUCKET", "telemetrie_peche_test")
os.environ.setdefault("REDIS_SENTINEL_1", "fake1")
os.environ.setdefault("REDIS_SENTINEL_2", "fake2")
os.environ.setdefault("REDIS_SENTINEL_3", "fake3")
os.environ.setdefault("REDIS_MASTER_NAME", "mymaster")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")

import pytest
from unittest.mock import MagicMock
import fakeredis
from mongomock_motor import AsyncMongoMockClient

import db as db_module
import cache_aside
import redis_client as redis_client_module

from app.services import (
    bateaux_service,
    pecheurs_service,
    captures_service,
    alertes_sos_service,
    telemetrie_service,
    auth_service,
)


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """Remplace le client Mongo par une base en mémoire, réinitialisée à chaque test."""
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["smart_fishing_test"]

    asyncio.get_event_loop().run_until_complete(
        mock_db.pecheurs.create_index("numero_licence", unique=True)
    )
    asyncio.get_event_loop().run_until_complete(
        mock_db.utilisateurs.create_index("username", unique=True)
    )

    monkeypatch.setattr(db_module, "db", mock_db)
    monkeypatch.setattr(bateaux_service, "db", mock_db)
    monkeypatch.setattr(pecheurs_service, "db", mock_db)
    monkeypatch.setattr(captures_service, "db", mock_db)
    monkeypatch.setattr(alertes_sos_service, "db", mock_db)
    monkeypatch.setattr(auth_service, "db", mock_db)

    yield mock_db


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Remplace Redis (Sentinel inclus) par un client en mémoire, vidé après chaque test."""
    fake = fakeredis.FakeStrictRedis(decode_responses=True)

    monkeypatch.setattr(cache_aside, "get_redis_master", lambda: fake)
    monkeypatch.setattr(cache_aside, "get_redis_replica", lambda: fake)
    monkeypatch.setattr(redis_client_module, "get_redis_master", lambda: fake)
    monkeypatch.setattr(redis_client_module, "get_redis_replica", lambda: fake)

    yield fake
    fake.flushall()


@pytest.fixture(autouse=True)
def mock_influx(monkeypatch):
    """
    Remplace les clients InfluxDB par des MagicMock. Par défaut, une requête
    renvoie une liste vide (aucune donnée) ; chaque test peut redéfinir
    mock_influx["query"].query.return_value pour simuler des points précis.
    """
    mock_write = MagicMock()
    mock_query = MagicMock()
    mock_query.query.return_value = []

    monkeypatch.setattr(db_module, "influx_write_api", mock_write)
    monkeypatch.setattr(db_module, "influx_query_api", mock_query)
    monkeypatch.setattr(bateaux_service, "influx_query_api", mock_query)
    monkeypatch.setattr(telemetrie_service, "influx_write_api", mock_write)
    monkeypatch.setattr(telemetrie_service, "influx_query_api", mock_query)

    yield {"write": mock_write, "query": mock_query}


@pytest.fixture
def client():
    """Client de test FastAPI (utilise les mocks ci-dessus via les autouse fixtures)."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def token_pour(client, mock_mongo):
    """
    Fabrique de tokens : token_pour("admin")("mon_admin") crée un utilisateur
    avec ce rôle (directement en base, sans passer par l'endpoint, pour éviter
    le problème de l'oeuf et de la poule sur les rôles admin/autorite) puis se
    connecte réellement via /auth/login pour obtenir un vrai token.
    """
    def _fabrique(role: str):
        def _pour(username: str, password: str = "motdepasse123", id_pecheur: str = None):
            asyncio.get_event_loop().run_until_complete(
                auth_service.creer_utilisateur(username, password, role, id_pecheur)
            )
            resp = client.post("/auth/login", data={"username": username, "password": password})
            assert resp.status_code == 200, resp.text
            token = resp.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return _pour
    return _fabrique


@pytest.fixture
def admin_headers(token_pour):
    return token_pour("admin")("admin_test")


@pytest.fixture
def creer_bateau(client, admin_headers):
    """Raccourci utilisé par presque tous les tests : crée un pêcheur + un bateau, renvoie l'id du bateau."""
    def _creer(numero_licence: str = "LIC-TEST"):
        resp = client.post("/pecheurs", json={
            "nom_complet": "Pêcheur Test",
            "telephone": "0700000000",
            "numero_licence": numero_licence,
        }, headers=admin_headers)
        assert resp.status_code == 201, resp.text
        id_pecheur = resp.json()["id"]

        resp = client.post("/bateaux", json={
            "nom": "Bateau Test",
            "id_pecheur_proprietaire": id_pecheur,
            "numero_immatriculation": f"IMMAT-{numero_licence}",
            "capacite_kg": 500,
        }, headers=admin_headers)
        assert resp.status_code == 201, resp.text
        return resp.json()["id"]

    return _creer