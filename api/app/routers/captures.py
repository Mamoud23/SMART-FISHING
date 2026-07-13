from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from app.models.capture import CaptureCreate, CaptureOut, StatistiquesCaptures
from app.services import captures_service, bateaux_service
from app.dependencies import exiger_role
from app.models.auth import Role

router = APIRouter(prefix="/captures", tags=["Captures"])


@router.get("", response_model=list[CaptureOut])
async def get_captures(
    id_bateau: Optional[str] = None,
    depuis: Optional[datetime] = None,
    jusqu_a: Optional[datetime] = None,
):
    return await captures_service.lister_captures(id_bateau=id_bateau, depuis=depuis, jusqu_a=jusqu_a)


@router.get("/statistiques", response_model=list[StatistiquesCaptures])
async def get_statistiques(
    id_bateau: Optional[str] = None,
    depuis: Optional[datetime] = None,
    jusqu_a: Optional[datetime] = None,
):
    """Totaux par espèce (poids, quantité, nombre de captures), filtrable par bateau et période."""
    return await captures_service.statistiques_par_espece(id_bateau=id_bateau, depuis=depuis, jusqu_a=jusqu_a)


@router.get("/{id_capture}", response_model=CaptureOut)
async def get_capture(id_capture: str):
    capture = await captures_service.obtenir_capture(id_capture)
    if not capture:
        raise HTTPException(status_code=404, detail="Capture introuvable")
    return capture


@router.post("", response_model=CaptureOut, status_code=201)
async def creer_capture(capture: CaptureCreate, _=Depends(exiger_role(Role.pecheur, Role.admin))):
    """
    Créée normalement par Node-RED dès qu'un message arrive sur le topic MQTT
    fishing/boat/+/catch (mode événementiel, déclenché par le pêcheur).
    """
    bateau = await bateaux_service.obtenir_bateau(capture.id_bateau)
    if not bateau:
        raise HTTPException(status_code=404, detail="Bateau introuvable")

    return await captures_service.creer_capture(capture.model_dump())