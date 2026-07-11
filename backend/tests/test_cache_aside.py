from cache_aside import get_or_set, invalidate


def test_get_or_set_ecrit_en_cache_au_premier_appel(mock_redis):
    compteur = {"appels": 0}

    def fetch():
        compteur["appels"] += 1
        return {"valeur": 42}

    resultat_1 = get_or_set("test:cle", fetch, ttl=60)
    resultat_2 = get_or_set("test:cle", fetch, ttl=60)

    assert resultat_1 == {"valeur": 42}
    assert resultat_2 == {"valeur": 42}
    assert compteur["appels"] == 1  # 2e appel servi depuis le cache, fetch_fn pas rappelée


def test_invalidate_force_un_nouveau_fetch(mock_redis):
    compteur = {"appels": 0}

    def fetch():
        compteur["appels"] += 1
        return {"valeur": compteur["appels"]}

    get_or_set("test:cle2", fetch, ttl=60)
    invalidate("test:cle2")
    get_or_set("test:cle2", fetch, ttl=60)

    assert compteur["appels"] == 2


def test_get_or_set_degrade_gracieusement_si_redis_indisponible(monkeypatch):
    """Si Redis est en panne, l'API doit continuer à fonctionner en lisant directement la source."""
    import cache_aside

    def redis_en_panne():
        raise ConnectionError("Redis indisponible (simulation)")

    monkeypatch.setattr(cache_aside, "get_redis_master", redis_en_panne)
    monkeypatch.setattr(cache_aside, "get_redis_replica", redis_en_panne)

    resultat = get_or_set("test:cle3", lambda: {"valeur": "secours"}, ttl=60)
    assert resultat == {"valeur": "secours"}