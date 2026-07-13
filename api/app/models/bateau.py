"""
Schémas Pydantic pour la ressource "bateau".

- BateauCreate  : ce que le client envoie pour créer un bateau (POST)
- BateauUpdate  : ce que le client envoie pour modifier un bateau (PATCH), tout optionnel
- BateauOut     : ce que l'API renvoie au client (inclut l'id, jamais de champ interne sensible)
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class StatutBateau(str, Enum):
    actif = "actif"
    en_maintenance = "en_maintenance"
    hors_service = "hors_service"


class BateauCreate(BaseModel):
    nom: str
    id_pecheur_proprietaire: str
    numero_immatriculation: str
    capacite_kg: float = Field(gt=0, description="Capacité de charge en kilogrammes")


class BateauUpdate(BaseModel):
    nom: Optional[str] = None
    statut: Optional[StatutBateau] = None
    capacite_kg: Optional[float] = Field(default=None, gt=0)


class BateauOut(BaseModel):
    id: str = Field(validation_alias="_id")
    nom: str
    id_pecheur_proprietaire: str
    numero_immatriculation: str
    capacite_kg: float
    statut: StatutBateau
    derniere_zone_connue: Optional[str] = None
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PositionBateau(BaseModel):
    id_bateau: str
    lat: float
    lng: float
    vitesse: Optional[float] = None
    horodatage: datetime