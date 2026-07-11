"""
Schémas Pydantic pour la ressource "capture" (capteur 4 du document de
justification des capteurs).

Particularité par rapport aux autres capteurs : mode événementiel (déclenché
par le pêcheur au moment de la capture) et non à fréquence fixe — donc stocké
dans MongoDB (collection captures) plutôt que dans InfluxDB, contrairement à
la télémétrie.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class GPSCapture(BaseModel):
    lat: float
    lng: float


class CaptureCreate(BaseModel):
    """
    Capteur 4 — mode événementiel, topic fishing/boat/+/catch.
    Enjeu sécurité IoT : la falsification des données de capture peut corrompre
    les statistiques nationales (MIRAH), fausser les quotas et favoriser la
    fraude économique. D'où l'intérêt d'une validation stricte des champs ici.
    """
    id_bateau: str
    espece: str
    poids_kg: float = Field(gt=0)
    quantite: int = Field(gt=0)
    gps_a_la_capture: GPSCapture
    horodatage: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class CaptureOut(BaseModel):
    id: str = Field(validation_alias="_id")
    id_bateau: str
    espece: str
    poids_kg: float
    quantite: int
    gps_a_la_capture: GPSCapture
    horodatage: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class StatistiquesCaptures(BaseModel):
    """Réponse de l'endpoint d'agrégation (total par espèce, par bateau, etc.)."""
    espece: str
    poids_total_kg: float
    quantite_totale: int
    nombre_captures: int