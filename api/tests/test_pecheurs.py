def test_creer_pecheur(client, admin_headers):
    resp = client.post("/pecheurs", json={
        "nom_complet": "Kouadio N'Guessan",
        "telephone": "0700000000",
        "numero_licence": "PECH-UNIQUE-1",
    }, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["bateaux"] == []
    assert data["role"] == "capitaine"


def test_creer_pecheur_sans_token_refuse(client):
    resp = client.post("/pecheurs", json={
        "nom_complet": "X", "telephone": "07", "numero_licence": "PECH-X",
    })
    assert resp.status_code == 401


def test_creer_pecheur_avec_role_pecheur_refuse(client, token_pour):
    """Seul un admin peut créer une fiche pêcheur (acte administratif)."""
    headers = token_pour("pecheur")("simple_pecheur")
    resp = client.post("/pecheurs", json={
        "nom_complet": "X", "telephone": "07", "numero_licence": "PECH-Y",
    }, headers=headers)
    assert resp.status_code == 403


def test_licence_dupliquee_rejetee(client, admin_headers):
    resp = client.post("/pecheurs", json={
        "nom_complet": "A", "telephone": "07", "numero_licence": "DUP-1",
    }, headers=admin_headers)
    assert resp.status_code == 201

    resp = client.post("/pecheurs", json={
        "nom_complet": "B", "telephone": "08", "numero_licence": "DUP-1",
    }, headers=admin_headers)
    assert resp.status_code == 409


def test_modifier_pecheur_par_admin(client, admin_headers):
    resp = client.post("/pecheurs", json={
        "nom_complet": "A", "telephone": "07", "numero_licence": "MOD-1",
    }, headers=admin_headers)
    id_pecheur = resp.json()["id"]

    resp = client.patch(f"/pecheurs/{id_pecheur}", json={"telephone": "0900000000"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["telephone"] == "0900000000"


def test_modifier_son_propre_profil_autorise(client, admin_headers, token_pour):
    """Un pêcheur doit pouvoir modifier SON PROPRE profil (self-service)."""
    resp = client.post("/pecheurs", json={
        "nom_complet": "A", "telephone": "07", "numero_licence": "SELF-1",
    }, headers=admin_headers)
    id_pecheur = resp.json()["id"]

    headers_pecheur = token_pour("pecheur")("user_self_1", id_pecheur=id_pecheur)
    resp = client.patch(f"/pecheurs/{id_pecheur}", json={"telephone": "0911111111"}, headers=headers_pecheur)
    assert resp.status_code == 200
    assert resp.json()["telephone"] == "0911111111"


def test_modifier_profil_dautrui_refuse(client, admin_headers, token_pour):
    """Un pêcheur ne doit PAS pouvoir modifier le profil d'un autre pêcheur."""
    resp = client.post("/pecheurs", json={
        "nom_complet": "A", "telephone": "07", "numero_licence": "SELF-2A",
    }, headers=admin_headers)
    id_pecheur_a = resp.json()["id"]

    resp = client.post("/pecheurs", json={
        "nom_complet": "B", "telephone": "08", "numero_licence": "SELF-2B",
    }, headers=admin_headers)
    id_pecheur_b = resp.json()["id"]

    headers_pecheur_a = token_pour("pecheur")("user_self_2", id_pecheur=id_pecheur_a)
    resp = client.patch(f"/pecheurs/{id_pecheur_b}", json={"telephone": "0900000000"}, headers=headers_pecheur_a)
    assert resp.status_code == 403


def test_pecheur_introuvable(client):
    resp = client.get("/pecheurs/000000000000000000000000")
    assert resp.status_code == 404