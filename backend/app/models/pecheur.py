from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class RolePecheur(str, Enum):
    capitaine = "capitaine"
    equipage = "equipage"

class PecheurCreate(BaseModel):
    nom_complet: str
    telephone: str
    numero_licence: str
    role: RolePecheur = RolePecheur.capitaine

class PecheurUpdate(BaseModel):
    nom_complet: Optional[str] = None
    telephone: Optional[str] = None
    role: Optional[RolePecheur] = None

class PecheurOut(BaseModel):
    # validation_alias lit '_id' depuis la DB, mais FastAPI affichera 'id' dans le JSON
    id: str = Field(validation_alias="_id") 
    nom_complet: str
    telephone: str
    numero_licence: str
    bateaux: list[str] = []
    role: RolePecheur
    date_creation: datetime

    # Nouvelle syntaxe Pydantic V2 pour la configuration
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )