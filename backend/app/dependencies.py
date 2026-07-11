from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decoder_access_token
from app.models.auth import TokenData, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    exception_auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou expirés",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decoder_access_token(token)
    if payload is None:
        raise exception_auth

    username = payload.get("sub")
    role = payload.get("role")
    if username is None or role is None:
        raise exception_auth

    return TokenData(username=username, role=role, id_pecheur=payload.get("id_pecheur"))


def exiger_role(*roles_autorises: Role):
    """
    Dépendance paramétrable : exiger_role(Role.admin, Role.autorite) protège un
    endpoint pour que seuls ces rôles puissent y accéder.
    """
    async def verifier(utilisateur: TokenData = Depends(get_current_user)) -> TokenData:
        if utilisateur.role not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès réservé aux rôles : {', '.join(r.value for r in roles_autorises)}",
            )
        return utilisateur
    return verifier