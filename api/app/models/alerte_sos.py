from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class StatutAlerte(str, Enum):
    ouverte = "ouverte"
    prise_en_charge = "prise_en_charge"
    resolue = "resolue"


class GpsPoint(BaseModel):
    lat: float
    lng: float


class AlerteSosCreate(BaseModel):
    id_bateau: str
    gps: GpsPoint


class AlerteSosOut(BaseModel):
    id: str = Field(validation_alias="_id")
    id_bateau: str
    horodatage: datetime
    gps: GpsPoint
    statut: StatutAlerte
    resolue_par: Optional[str] = None
    date_resolution: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)