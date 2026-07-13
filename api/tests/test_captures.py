def test_creer_capture_et_statistiques(client, creer_bateau, admin_headers):
    id_bateau = creer_bateau("LIC-CAP-1")

    for poids, quantite in [(10, 2), (5, 1)]:
        resp = client.post("/captures", json={
            "id_bateau": id_bateau,
            "espece": "Thiof",
            "poids_kg": poids,
            "quantite": quantite,
            "gps_a_la_capture": {"lat": 5.3, "lng": -4.0},
        }, headers=admin_headers)
        assert resp.status_code == 201

    resp = client.get("/captures", params={"id_bateau": id_bateau})
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp = client.get("/captures/statistiques", params={"id_bateau": id_bateau})
    assert resp.status_code == 200
    stats = resp.json()
    thiof = next(s for s in stats if s["espece"] == "Thiof")
    assert thiof["poids_total_kg"] == 15
    assert thiof["quantite_totale"] == 3
    assert thiof["nombre_captures"] == 2


def test_capture_sans_token_refuse(client, creer_bateau):
    id_bateau = creer_bateau("LIC-CAP-1B")
    resp = client.post("/captures", json={
        "id_bateau": id_bateau,
        "espece": "Thiof",
        "poids_kg": 1,
        "quantite": 1,
        "gps_a_la_capture": {"lat": 0, "lng": 0},
    })
    assert resp.status_code == 401


def test_capture_bateau_inexistant(client, admin_headers):
    resp = client.post("/captures", json={
        "id_bateau": "000000000000000000000000",
        "espece": "Inconnue",
        "poids_kg": 1,
        "quantite": 1,
        "gps_a_la_capture": {"lat": 0, "lng": 0},
    }, headers=admin_headers)
    assert resp.status_code == 404


def test_capture_poids_negatif_rejete(client, creer_bateau, admin_headers):
    """Validation Pydantic : poids_kg doit être > 0 (protection contre données falsifiées)."""
    id_bateau = creer_bateau("LIC-CAP-2")
    resp = client.post("/captures", json={
        "id_bateau": id_bateau,
        "espece": "Thiof",
        "poids_kg": -5,
        "quantite": 1,
        "gps_a_la_capture": {"lat": 0, "lng": 0},
    }, headers=admin_headers)
    assert resp.status_code == 422