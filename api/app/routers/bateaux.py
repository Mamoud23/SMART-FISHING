from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from app.models.bateau import BateauCreate, BateauUpdate, BateauOut, PositionBateau
from app.services import bateaux_service
from app.dependencies import exiger_role
from app.models.auth import Role

router = APIRouter(prefix="/bateaux", tags=["Bateaux"])


@router.get("", response_model=list[BateauOut])
async def get_bateaux(statut: Optional[str] = None):
    return await bateaux_service.lister_bateaux(statut=statut)


@router.get("/{id_bateau}", response_model=BateauOut)
async def get_bateau(id_bateau: str):
    bateau = await bateaux_service.obtenir_bateau(id_bateau)
    if not bateau:
        raise HTTPException(status_code=404, detail="Bateau introuvable")
    return bateau


@router.post("", response_model=BateauOut, status_code=201)
async def creer_bateau(bateau: BateauCreate, _=Depends(exiger_role(Role.pecheur, Role.admin))):
    cree = await bateaux_service.creer_bateau(bateau.model_dump())
    return cree


@router.patch("/{id_bateau}", response_model=BateauOut)
async def modifier_bateau(id_bateau: str, updates: BateauUpdate, _=Depends(exiger_role(Role.pecheur, Role.admin))):
    existant = await bateaux_service.obtenir_bateau(id_bateau)
    if not existant:
        raise HTTPException(status_code=404, detail="Bateau introuvable")
    return await bateaux_service.modifier_bateau(id_bateau, updates.model_dump())


@router.get("/{id_bateau}/position", response_model=PositionBateau)
async def get_position_bateau(id_bateau: str):
    existant = await bateaux_service.obtenir_bateau(id_bateau)
    if not existant:
        raise HTTPException(status_code=404, detail="Bateau introuvable")

    position = bateaux_service.obtenir_derniere_position(id_bateau)
    if not position:
        raise HTTPException(status_code=404, detail="Aucune position connue pour ce bateau")
    return position