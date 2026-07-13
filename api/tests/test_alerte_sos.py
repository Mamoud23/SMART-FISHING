import json


def test_creer_prendre_en_charge_et_resoudre_alerte(client, creer_bateau, admin_headers):
    id_bateau = creer_bateau("LIC-SOS-1")

    # création : volontairement ouverte (déclenchée par un capteur/Node-RED, pas un utilisateur)
    resp = client.post("/alertes-sos", json={
        "id_bateau": id_bateau,
        "gps": {"lat": 5.30, "lng": -4.05},
    })
    assert resp.status_code == 201
    alerte = resp.json()
    assert alerte["statut"] == "ouverte"
    id_alerte = alerte["id"]

    resp = client.get("/alertes-sos", params={"statut": "ouverte"})
    assert any(a["id"] == id_alerte for a in resp.json())

    # prendre en charge / résoudre : réservé autorite/admin
    resp = client.post(f"/alertes-sos/{id_alerte}/prendre-en-charge", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["statut"] == "prise_en_charge"

    resp = client.post(
        f"/alertes-sos/{id_alerte}/resoudre",
        params={"resolue_par": "Toure"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["statut"] == "resolue"
    assert resp.json()["resolue_par"] == "Toure"


def test_resoudre_sans_token_refuse(client, creer_bateau):
    id_bateau = creer_bateau("LIC-SOS-1B")
    resp = client.post("/alertes-sos", json={"id_bateau": id_bateau, "gps": {"lat": 1, "lng": 1}})
    id_alerte = resp.json()["id"]

    resp = client.post(f"/alertes-sos/{id_alerte}/prendre-en-charge")
    assert resp.status_code == 401


def test_resoudre_avec_role_pecheur_refuse(client, creer_bateau, token_pour):
    """Un pêcheur n'a pas le droit de résoudre une alerte SOS (réservé autorite/admin)."""
    id_bateau = creer_bateau("LIC-SOS-1C")
    resp = client.post("/alertes-sos", json={"id_bateau": id_bateau, "gps": {"lat": 1, "lng": 1}})
    id_alerte = resp.json()["id"]

    headers_pecheur = token_pour("pecheur")("pecheur_sos_test")
    resp = client.post(f"/alertes-sos/{id_alerte}/prendre-en-charge", headers=headers_pecheur)
    assert resp.status_code == 403


def test_alerte_introuvable(client, admin_headers):
    resp = client.post("/alertes-sos/000000000000000000000000/prendre-en-charge", headers=admin_headers)
    assert resp.status_code == 404


def test_nb_ouvertes(client, creer_bateau):
    id_bateau = creer_bateau("LIC-SOS-2")
    client.post("/alertes-sos", json={"id_bateau": id_bateau, "gps": {"lat": 1, "lng": 1}})

    resp = client.get("/alertes-sos/nb-ouvertes")
    assert resp.status_code == 200
    assert resp.json()["nb_ouvertes"] >= 1


def test_publication_pubsub_a_la_creation(client, creer_bateau, mock_redis):
    """Vérifie que la création d'une alerte publie bien sur le canal sos:alertes."""
    id_bateau = creer_bateau("LIC-SOS-3")

    pubsub = mock_redis.pubsub()
    pubsub.subscribe("sos:alertes")
    pubsub.get_message()  # consomme le message de confirmation d'abonnement

    resp = client.post("/alertes-sos", json={"id_bateau": id_bateau, "gps": {"lat": 2, "lng": 2}})
    assert resp.status_code == 201

    message = pubsub.get_message(timeout=1)
    assert message is not None
    assert message["type"] == "message"
    contenu = json.loads(message["data"])
    assert contenu["id_bateau"] == id_bateau