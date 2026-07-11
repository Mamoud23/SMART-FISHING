from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.models.auth import UtilisateurCreate, UtilisateurOut, Token, Role
from app.services import auth_service
from app.core.security import creer_access_token
from app.dependencies import exiger_role, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=UtilisateurOut, status_code=201)
async def register(utilisateur: UtilisateurCreate):
    """
    Inscription ouverte pour le rôle "pecheur" uniquement. Les rôles admin/autorite
    doivent être créés par un admin existant via POST /auth/register-privilegie
    (ou directement en base pour le tout premier admin, cf. README).
    """
    if utilisateur.role != Role.pecheur:
        raise HTTPException(
            status_code=403,
            detail="Seul un admin peut créer un compte avec le rôle admin ou autorite.",
        )
    try:
        return await auth_service.creer_utilisateur(
            utilisateur.username, utilisateur.password, utilisateur.role.value, utilisateur.id_pecheur
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/register-privilegie", response_model=UtilisateurOut, status_code=201)
async def register_privilegie(
    utilisateur: UtilisateurCreate,
    _: object = Depends(exiger_role(Role.admin)),
):
    """Réservé aux admins : permet de créer un compte admin ou autorite."""
    try:
        return await auth_service.creer_utilisateur(
            utilisateur.username, utilisateur.password, utilisateur.role.value, utilisateur.id_pecheur
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    utilisateur = await auth_service.authentifier(form_data.username, form_data.password)
    if not utilisateur:
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    token = creer_access_token({
        "sub": utilisateur["username"],
        "role": utilisateur["role"],
        "id_pecheur": utilisateur.get("id_pecheur"),
    })
    return Token(access_token=token)


@router.get("/moi", response_model=dict)
async def moi(utilisateur=Depends(get_current_user)):
    """Utile pour vérifier rapidement que le token fonctionne."""
    return utilisateur.model_dump()