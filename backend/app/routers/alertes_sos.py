from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from app.models.alerte_sos import AlerteSosCreate, AlerteSosOut
from app.services import alertes_sos_service
from app.dependencies import exiger_role
from app.models.auth import Role

router = APIRouter(prefix="/alertes-sos", tags=["Alertes SOS"])


@router.get("", response_model=list[AlerteSosOut])
async def get_alertes(statut: Optional[str] = None):
    return await alertes_sos_service.lister_alertes(statut=statut)


@router.get("/nb-ouvertes")
async def get_nb_ouvertes():
    """Compteur temps réel (cache 5s), pour un badge dashboard par exemple."""
    return await alertes_sos_service.compter_alertes_ouvertes()


@router.get("/{id_alerte}", response_model=AlerteSosOut)
async def get_alerte(id_alerte: str):
    alerte = await alertes_sos_service.obtenir_alerte(id_alerte)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte SOS introuvable")
    return alerte


@router.post("", response_model=AlerteSosOut, status_code=201)
async def creer_alerte(alerte: AlerteSosCreate):
    """
    Créée normalement par Node-RED dès qu'un message arrive sur le topic MQTT
    fishing/boat/+/sos. Exposée ici pour pouvoir tester avant que le broker
    MQTT + Node-RED soient branchés.
    """
    document = await alertes_sos_service.creer_alerte(
        id_bateau=alerte.id_bateau,
        gps=alerte.gps.model_dump(),
    )
    return document


@router.post("/{id_alerte}/prendre-en-charge", response_model=AlerteSosOut)
async def prendre_en_charge(id_alerte: str, _=Depends(exiger_role(Role.autorite, Role.admin))):
    alerte = await alertes_sos_service.prendre_en_charge(id_alerte)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte SOS introuvable")
    return alerte


@router.post("/{id_alerte}/resoudre", response_model=AlerteSosOut)
async def resoudre(id_alerte: str, resolue_par: Optional[str] = None, _=Depends(exiger_role(Role.autorite, Role.admin))):
    alerte = await alertes_sos_service.resoudre(id_alerte, resolue_par=resolue_par)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte SOS introuvable")
    return alerte