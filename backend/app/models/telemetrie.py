"""
Schémas Pydantic pour la télémétrie (capteurs 2, 3, 6, 7 du document de
justification). Le capteur 1 (GPS) est déjà couvert par PositionBateau dans
app/models/bateau.py, et le capteur 5 (SOS) par app/models/alerte_sos.py.

Chaque docstring de classe rappelle l'enjeu de sécurité IoT identifié dans le
document, pour garder la traçabilité entre la justification métier et le code.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TemperatureEau(BaseModel):
    """
    Capteur 2 — fréquence 5 min, topic fishing/boat/+/water_temp.
    Enjeu sécurité IoT : des données falsifiées orientent les pêcheurs vers de
    mauvaises zones de pêche (pertes économiques, exploitation irrationnelle).
    """
    id_bateau: str
    temp_celsius: float
    horodatage: datetime


class Vent(BaseModel):
    """
    Capteur 3 — fréquence 5 min, topic fishing/boat/+/wind.
    Une pirogue artisanale peut chavirer au-delà de ~30 km/h de vent.
    Enjeu sécurité IoT : des données interceptées/modifiées peuvent donner une
    fausse sécurité et inciter un pêcheur à rester en mer pendant une tempête.
    """
    id_bateau: str
    vitesse_kmh: float
    direction_deg: float = Field(ge=0, lt=360)
    horodatage: datetime

    @property
    def alerte_vent_fort(self) -> bool:
        """Seuil de vigilance basé sur le document (risque de chavirement au-delà de 30 km/h)."""
        return self.vitesse_kmh > 30


class Turbidite(BaseModel):
    """
    Capteur 6 — fréquence 10 min, topic fishing/boat/+/turbidity.
    Détecte rejets industriels (ports d'Abidjan/San-Pedro) et sédiments après
    de fortes pluies près des estuaires (Comoé, Bandama).
    Enjeu sécurité IoT : des données falsifiées peuvent orienter les pêcheurs
    vers des zones polluées à leur insu (risque sanitaire).
    """
    id_bateau: str
    ntu: float = Field(ge=0, description="Unité de turbidité néphélométrique")
    horodatage: datetime


class Inclinaison(BaseModel):
    """
    Capteur 7 — fréquence 1 min, topic fishing/boat/+/tilt.
    Filet de sécurité ultime : détection automatique de chavirement, sans
    intervention du pêcheur (complémentaire au bouton SOS, actif lui aussi).
    Enjeu sécurité IoT : désactiver ce capteur par une attaque supprime le
    dernier filet de sécurité — un naufrage peut passer inaperçu des secours.
    """
    id_bateau: str
    angle_deg: float
    risque_chavirement: bool
    horodatage: datetime