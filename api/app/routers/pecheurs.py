from fastapi import APIRouter, HTTPException, Depends

from app.models.pecheur import PecheurCreate, PecheurUpdate, PecheurOut
from app.services import pecheurs_service
from app.dependencies import exiger_role, get_current_user
from app.models.auth import Role, TokenData

router = APIRouter(prefix="/pecheurs", tags=["Pêcheurs"])


@router.get("", response_model=list[PecheurOut])
async def get_pecheurs():
    return await pecheurs_service.lister_pecheurs()


@router.get("/{id_pecheur}", response_model=PecheurOut)
async def get_pecheur(id_pecheur: str):
    pecheur = await pecheurs_service.obtenir_pecheur(id_pecheur)
    if not pecheur:
        raise HTTPException(status_code=404, detail="Pêcheur introuvable")
    return pecheur


@router.post("", response_model=PecheurOut, status_code=201)
async def creer_pecheur(pecheur: PecheurCreate, _=Depends(exiger_role(Role.admin))):
    """
    Réservé aux admins : l'enregistrement officiel d'un pêcheur (numéro de
    licence) est un acte administratif, pas une auto-inscription.
    """
    try:
        return await pecheurs_service.creer_pecheur(pecheur.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{id_pecheur}", response_model=PecheurOut)
async def modifier_pecheur(
    id_pecheur: str,
    updates: PecheurUpdate,
    utilisateur: TokenData = Depends(get_current_user),
):
    """Modifiable par un admin, ou par le pêcheur lui-même (self-service)."""
    if utilisateur.role != Role.admin and utilisateur.id_pecheur != id_pecheur:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez modifier que votre propre profil.",
        )

    existant = await pecheurs_service.obtenir_pecheur(id_pecheur)
    if not existant:
        raise HTTPException(status_code=404, detail="Pêcheur introuvable")
    return await pecheurs_service.modifier_pecheur(id_pecheur, updates.model_dump())