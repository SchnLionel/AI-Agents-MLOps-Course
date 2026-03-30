import logging
import random
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class WeatherInput(BaseModel):
    """Schéma d'entrée pour l'outil Météo."""
    location: str = Field(description="Le nom de la ville pour laquelle obtenir la météo.")

def get_weather(location: str) -> str:
    """
    Simule la récupération de la météo pour une ville donnée.
    Renvoie une température aléatoire pour la démonstration.
    """
    logger.info(f"Outil 'get_weather' appelé pour la ville : '{location}'")
    
    # Simulation de données météo
    villes_coords = {
        "Paris": 15,
        "Lyon": 18,
        "Marseille": 22,
        "London": 12,
        "New York": 20,
        "Tokyo": 25
    }
    
    # Si la ville est connue, on donne une température fixe + un petit aléa
    # Sinon, on donne une valeur aléatoire entre 0 et 35
    base_temp = villes_coords.get(location, random.randint(0, 35))
    temp = base_temp + random.uniform(-2, 2)
    
    conditions = ["Ensoleillé", "Nuageux", "Pluvieux", "Orageux", "Partiellement nuageux"]
    condition = random.choice(conditions)
    
    result = {
        "location": location,
        "temperature": round(temp, 1),
        "condition": condition,
        "unit": "Celsius"
    }
    
    logger.info(f"Météo simulée pour '{location}': {result}")
    return str(result)
