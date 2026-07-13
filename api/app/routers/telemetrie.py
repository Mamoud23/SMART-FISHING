from fastapi import APIRouter, HTTPException, Depends

from app.models.telemetrie import TemperatureEau, Vent, Turbidite, Inclinaison
from app.services import telemetrie_service, bateaux_service
from app.dependencies import exiger_role
from app.models.auth import Role

router = APIRouter(prefix="/telemetrie", tags=["Télémétrie"])

# Écriture réservée à pecheur/admin (représente le bateau/dispositif enregistré) ;
# lecture laissée publique, comme pour bateaux/captures.
_ecriture_autorisee = Depends(exiger_role(Role.pecheur, Role.admin))


async def _verifier_bateau_existe(id_bateau: str):
    bateau = await bateaux_service.obtenir_bateau(id_bateau)
    if not bateau:
        raise HTTPException(status_code=404, detail="Bateau introuvable")


# ---------- Température de l'eau ----------

@router.post("/temperature-eau", status_code=201)
async def poster_temperature_eau(data: TemperatureEau, _=_ecriture_autorisee):
    await _verifier_bateau_existe(data.id_bateau)
    return await telemetrie_service.enregistrer_temperature_eau(data)


@router.get("/{id_bateau}/temperature-eau")
async def get_historique_temperature_eau(id_bateau: str, depuis: str = "-24h"):
    await _verifier_bateau_existe(id_bateau)
    return await telemetrie_service.historique_temperature_eau(id_bateau, depuis)


# ---------- Vent ----------

@router.post("/vent", status_code=201)
async def poster_vent(data: Vent, _=_ecriture_autorisee):
    await _verifier_bateau_existe(data.id_bateau)
    return await telemetrie_service.enregistrer_vent(data)


@router.get("/{id_bateau}/vent")
async def get_historique_vent(id_bateau: str, depuis: str = "-24h"):
    await _verifier_bateau_existe(id_bateau)
    return await telemetrie_service.historique_vent(id_bateau, depuis)


# ---------- Turbidité ----------

@router.post("/turbidite", status_code=201)
async def poster_turbidite(data: Turbidite, _=_ecriture_autorisee):
    await _verifier_bateau_existe(data.id_bateau)
    return await telemetrie_service.enregistrer_turbidite(data)


@router.get("/{id_bateau}/turbidite")
async def get_historique_turbidite(id_bateau: str, depuis: str = "-24h"):
    await _verifier_bateau_existe(id_bateau)
    return await telemetrie_service.historique_turbidite(id_bateau, depuis)


# ---------- Inclinaison (avec SOS automatique si risque_chavirement) ----------

@router.post("/inclinaison", status_code=201)
async def poster_inclinaison(data: Inclinaison, _=_ecriture_autorisee):
    """
    Si risque_chavirement=True, une alerte SOS est créée automatiquement
    (cf. document de justification : filet de sécurité ultime, sans
    intervention du pêcheur). La réponse indique l'id de l'alerte créée,
    le cas échéant, dans le champ "alerte_sos_creee".
    """
    await _verifier_bateau_existe(data.id_bateau)
    return await telemetrie_service.enregistrer_inclinaison(data)


@router.get("/{id_bateau}/inclinaison")
async def get_historique_inclinaison(id_bateau: str, depuis: str = "-24h"):
    await _verifier_bateau_existe(id_bateau)
    return await telemetrie_service.historique_inclinaison(id_bateau, depuis)