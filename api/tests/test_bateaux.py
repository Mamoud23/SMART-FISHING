def test_creer_et_lister_bateau(client, creer_bateau):
    id_bateau = creer_bateau("LIC-BAT-1")

    resp = client.get("/bateaux")
    assert resp.status_code == 200
    assert any(b["id"] == id_bateau for b in resp.json())

    resp = client.get(f"/bateaux/{id_bateau}")
    assert resp.status_code == 200
    assert resp.json()["statut"] == "actif"


def test_bateau_introuvable(client):
    resp = client.get("/bateaux/000000000000000000000000")
    assert resp.status_code == 404


def test_bateau_id_invalide(client):
    """Un id qui n'est même pas un ObjectId valide doit renvoyer 404, pas planter."""
    resp = client.get("/bateaux/id-completement-invalide")
    assert resp.status_code == 404


def test_pecheur_a_bien_le_bateau_dans_sa_liste(client, creer_bateau):
    id_bateau = creer_bateau("LIC-BAT-2")

    resp = client.get("/bateaux")
    bateau = next(b for b in resp.json() if b["id"] == id_bateau)
    id_pecheur = bateau["id_pecheur_proprietaire"]

    resp = client.get(f"/pecheurs/{id_pecheur}")
    assert id_bateau in resp.json()["bateaux"]


def test_modifier_bateau(client, creer_bateau, admin_headers):
    id_bateau = creer_bateau("LIC-BAT-3")

    resp = client.patch(f"/bateaux/{id_bateau}", json={"statut": "en_maintenance"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["statut"] == "en_maintenance"


def test_modifier_bateau_sans_token_refuse(client, creer_bateau):
    id_bateau = creer_bateau("LIC-BAT-3B")
    resp = client.patch(f"/bateaux/{id_bateau}", json={"statut": "en_maintenance"})
    assert resp.status_code == 401


def test_position_bateau_sans_donnee(client, creer_bateau, mock_influx):
    """Aucun point GPS inséré -> InfluxDB (mocké) renvoie vide -> 404 attendu."""
    id_bateau = creer_bateau("LIC-BAT-4")

    resp = client.get(f"/bateaux/{id_bateau}/position")
    assert resp.status_code == 404