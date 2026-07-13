import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return _pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    return _pwd_context.verify(mot_de_passe, hash_stocke)


def creer_access_token(donnees: dict, expire_minutes: Optional[int] = None) -> str:
    a_encoder = donnees.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes or EXPIRE_MINUTES)
    a_encoder["exp"] = expiration
    return jwt.encode(a_encoder, SECRET_KEY, algorithm=ALGORITHM)


def decoder_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None