"""
Logique métier pour la télémétrie (température eau, vent, turbidité, inclinaison).

Point critique (capteur 7 du document de justification) : une lecture
d'inclinaison avec risque_chavirement=True doit déclencher automatiquement une
alerte SOS, sans intervention du pêcheur — c'est le "filet de sécurité ultime"
mentionné dans le document.
"""

from datetime import datetime
from typing import Optional

from influxdb_client import Point

from db import influx_write_api, influx_query_api, INFLUX_BUCKET, INFLUX_ORG
from app.services import bateaux_service, alertes_sos_service

SEUIL_VENT_DANGEREUX_KMH = 30  # cf. document : risque de chavirement au-delà de ~30 km/h


def _ecrire_point(measurement: str, id_bateau: str, champs: dict, horodatage: datetime):
    point = Point(measurement).tag("id_bateau", id_bateau).time(horodatage)
    for cle, valeur in champs.items():
        point = point.field(cle, valeur)
    influx_write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)


def _lire_historique(measurement: str, id_bateau: str, depuis: str = "-24h", limite: int = 100) -> list[dict]:
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {depuis})
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> filter(fn: (r) => r.id_bateau == "{id_bateau}")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: {limite})
    '''
    tables = influx_query_api.query(query, org=INFLUX_ORG)

    points_par_heure = {}
    for table in tables:
        for record in table.records:
            horodatage = record.get_time()
            if horodatage not in points_par_heure:
                points_par_heure[horodatage] = {"id_bateau": id_bateau, "horodatage": horodatage.isoformat()}
            points_par_heure[horodatage][record.get_field()] = record.get_value()

    return sorted(points_par_heure.values(), key=lambda p: p["horodatage"], reverse=True)


# ---------- Température de l'eau (capteur 2) ----------

async def enregistrer_temperature_eau(data) -> dict:
    _ecrire_point("temperature_eau", data.id_bateau, {"temp_celsius": data.temp_celsius}, data.horodatage)
    return data.model_dump()


async def historique_temperature_eau(id_bateau: str, depuis: str = "-24h") -> list[dict]:
    return _lire_historique("temperature_eau", id_bateau, depuis)


# ---------- Vent (capteur 3) ----------

async def enregistrer_vent(data) -> dict:
    _ecrire_point(
        "vent",
        data.id_bateau,
        {"vitesse_kmh": data.vitesse_kmh, "direction_deg": data.direction_deg},
        data.horodatage,
    )
    resultat = data.model_dump()
    resultat["alerte_vent_fort"] = data.vitesse_kmh > SEUIL_VENT_DANGEREUX_KMH
    return resultat


async def historique_vent(id_bateau: str, depuis: str = "-24h") -> list[dict]:
    return _lire_historique("vent", id_bateau, depuis)


# ---------- Turbidité (capteur 6) ----------

async def enregistrer_turbidite(data) -> dict:
    _ecrire_point("turbidite", data.id_bateau, {"ntu": data.ntu}, data.horodatage)
    return data.model_dump()


async def historique_turbidite(id_bateau: str, depuis: str = "-24h") -> list[dict]:
    return _lire_historique("turbidite", id_bateau, depuis)


# ---------- Inclinaison (capteur 7) — avec déclenchement SOS automatique ----------

async def enregistrer_inclinaison(data) -> dict:
    _ecrire_point(
        "inclinaison",
        data.id_bateau,
        {"angle_deg": data.angle_deg, "risque_chavirement": data.risque_chavirement},
        data.horodatage,
    )

    resultat = data.model_dump()
    resultat["alerte_sos_creee"] = None

    if data.risque_chavirement:
        # Filet de sécurité ultime (cf. document) : SOS automatique, sans
        # intervention du pêcheur. On récupère la dernière position GPS connue
        # (cache-aside déjà en place) pour localiser le naufrage potentiel.
        position = bateaux_service.obtenir_derniere_position(data.id_bateau)
        if position:
            gps = {"lat": position["lat"], "lng": position["lng"]}
        else:
            gps = {"lat": 0.0, "lng": 0.0}
            print(f"[inclinaison] Position GPS inconnue pour {data.id_bateau}, SOS créé avec position par défaut.")

        alerte = await alertes_sos_service.creer_alerte(id_bateau=data.id_bateau, gps=gps)
        resultat["alerte_sos_creee"] = alerte["_id"]

    return resultat


async def historique_inclinaison(id_bateau: str, depuis: str = "-24h") -> list[dict]:
    return _lire_historique("inclinaison", id_bateau, depuis)