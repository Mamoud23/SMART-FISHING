def test_register_pecheur_ok(client):
    resp = client.post("/auth/register", json={
        "username": "nouveau_pecheur",
        "password": "motdepasse123",
        "role": "pecheur",
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "pecheur"


def test_register_role_admin_refuse(client):
    """L'inscription libre ne permet pas de se donner le rôle admin soi-même."""
    resp = client.post("/auth/register", json={
        "username": "faux_admin",
        "password": "motdepasse123",
        "role": "admin",
    })
    assert resp.status_code == 403


def test_register_username_deja_pris(client):
    payload = {"username": "duplique", "password": "motdepasse123", "role": "pecheur"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201

    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_identifiants_corrects(client):
    client.post("/auth/register", json={
        "username": "login_test", "password": "motdepasse123", "role": "pecheur",
    })
    resp = client.post("/auth/login", data={"username": "login_test", "password": "motdepasse123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_mot_de_passe_incorrect(client):
    client.post("/auth/register", json={
        "username": "login_test_2", "password": "motdepasse123", "role": "pecheur",
    })
    resp = client.post("/auth/login", data={"username": "login_test_2", "password": "mauvais"})
    assert resp.status_code == 401


def test_login_utilisateur_inexistant(client):
    resp = client.post("/auth/login", data={"username": "fantome", "password": "peu-importe"})
    assert resp.status_code == 401


def test_route_protegee_sans_token(client):
    resp = client.get("/auth/moi")
    assert resp.status_code == 401


def test_route_protegee_avec_token_invalide(client):
    resp = client.get("/auth/moi", headers={"Authorization": "Bearer token-invalide"})
    assert resp.status_code == 401


def test_route_protegee_avec_token_valide(client, admin_headers):
    resp = client.get("/auth/moi", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_register_privilegie_necessite_admin(client, token_pour):
    """Un pêcheur ne peut pas créer un compte admin/autorite, même via l'endpoint privilégié."""
    headers_pecheur = token_pour("pecheur")("simple_user_priv")
    resp = client.post("/auth/register-privilegie", json={
        "username": "tentative_admin", "password": "motdepasse123", "role": "admin",
    }, headers=headers_pecheur)
    assert resp.status_code == 403


def test_register_privilegie_avec_admin_fonctionne(client, admin_headers):
    resp = client.post("/auth/register-privilegie", json={
        "username": "nouvelle_autorite", "password": "motdepasse123", "role": "autorite",
    }, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["role"] == "autorite"