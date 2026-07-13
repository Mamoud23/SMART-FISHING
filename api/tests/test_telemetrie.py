HORODATAGE = "2026-07-10T10:00:00Z"


def test_vent_seuil_alerte(client, creer_bateau, admin_headers):
    id_bateau = creer_bateau("LIC-TEL-1")

    resp = client.post("/telemetrie/vent", json={
        "id_bateau": id_bateau, "vitesse_kmh": 35, "direction_deg": 180, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["alerte_vent_fort"] is True

    resp = client.post("/telemetrie/vent", json={
        "id_bateau": id_bateau, "vitesse_kmh": 10, "direction_deg": 90, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.json()["alerte_vent_fort"] is False


def test_telemetrie_sans_token_refuse(client, creer_bateau):
    id_bateau = creer_bateau("LIC-TEL-1B")
    resp = client.post("/telemetrie/vent", json={
        "id_bateau": id_bateau, "vitesse_kmh": 10, "direction_deg": 90, "horodatage": HORODATAGE,
    })
    assert resp.status_code == 401


def test_temperature_eau_enregistree(client, creer_bateau, admin_headers):
    id_bateau = creer_bateau("LIC-TEL-2")
    resp = client.post("/telemetrie/temperature-eau", json={
        "id_bateau": id_bateau, "temp_celsius": 27.5, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["temp_celsius"] == 27.5


def test_turbidite_enregistree(client, creer_bateau, admin_headers):
    id_bateau = creer_bateau("LIC-TEL-3")
    resp = client.post("/telemetrie/turbidite", json={
        "id_bateau": id_bateau, "ntu": 12.4, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["ntu"] == 12.4


def test_telemetrie_bateau_inexistant(client, admin_headers):
    resp = client.post("/telemetrie/temperature-eau", json={
        "id_bateau": "000000000000000000000000", "temp_celsius": 25, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.status_code == 404


# ---------- Le test le plus important de toute la suite ----------

def test_inclinaison_critique_declenche_sos_automatique(client, creer_bateau, admin_headers):
    """
    Règle métier tirée du document de justification des capteurs :
    un angle critique doit créer une alerte SOS automatiquement,
    SANS que le pêcheur ait pressé le bouton SOS.
    """
    id_bateau = creer_bateau("LIC-TEL-4")

    resp = client.post("/telemetrie/inclinaison", json={
        "id_bateau": id_bateau, "angle_deg": 47, "risque_chavirement": True, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["alerte_sos_creee"] is not None

    resp = client.get("/alertes-sos", params={"statut": "ouverte"})
    ids_ouvertes = [a["id"] for a in resp.json()]
    assert data["alerte_sos_creee"] in ids_ouvertes


def test_inclinaison_normale_ne_declenche_pas_sos(client, creer_bateau, admin_headers):
    """Contre-test : sans risque de chavirement, aucune alerte ne doit être créée."""
    id_bateau = creer_bateau("LIC-TEL-5")

    resp = client.post("/telemetrie/inclinaison", json={
        "id_bateau": id_bateau, "angle_deg": 5, "risque_chavirement": False, "horodatage": HORODATAGE,
    }, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["alerte_sos_creee"] is None