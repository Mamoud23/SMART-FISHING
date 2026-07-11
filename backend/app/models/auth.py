from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Role(str, Enum):
    admin = "admin"
    autorite = "autorite"       # autorités maritimes
    pecheur = "pecheur"


class UtilisateurCreate(BaseModel):
    username: str
    password: str = Field(min_length=8)
    role: Role = Role.pecheur
    id_pecheur: Optional[str] = None  # lien vers la fiche pêcheur, si role == pecheur


class UtilisateurOut(BaseModel):
    id: str = Field(alias="_id")
    username: str
    role: Role
    id_pecheur: Optional[str] = None
    date_creation: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str
    role: Role
    id_pecheur: Optional[str] = None