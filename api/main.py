#Imports
import logging
import os
from pathlib import Path
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Données de Validations de Titre de Transports",
    description="Une API sécurisée par clé pour servir les données de validations de titre de transport en Ile-de-France et de stations/gares."
)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API des données de validation de titre de transport en Ile-de-France !"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Data API"}


# Sécurité : Configuration de la clé API.

# Nom de l'en-tête HTTP que le client devra envoyer.
API_KEY_NAME = "X-API-Key"

# Stocker cette clé dans les variables d'environnement.
# Si la variable n'est pas définie, on utilise une clé par défaut.
API_KEY = os.getenv("MY_API_KEY", "ma_cle_secrete_123")

# Définir un schéma de sécurité pour FastAPI.
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    
    #Dépendance pour vérifier la validité de la clé API fournie.    
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide ou manquante."
        )
    return api_key



# Chargement des données.

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data" / "processed"

stations_data = []
#validations_data = []
validations_ligne_data = []

@app.on_event("startup")
def load_and_cache_data():
    global stations_data, validations_data, validations_ligne_data
    logger.info("Chargement et traitement des fichiers CSV en cours...")
    try:
        stations_data = pd.read_csv(DATA_DIR / "stations.csv").to_dict(orient="records")
        #validations_data = pd.read_csv(DATA_DIR / "validations.csv").to_dict(orient="records")
        validations_ligne_data = pd.read_csv(DATA_DIR / "validations_ligne.csv").to_dict(orient="records")
        logger.info("Données chargées et converties avec succès !")
    except FileNotFoundError as e:
        logger.error(f"Impossible de trouver les fichiers de données : {e}")
        raise e



# Endpoints sécurisés en ajoutant `dependencies=[Security(verify_api_key)]`, l'accès est bloqué sans clé valide.

@app.get(
        "/api/stations", 
        dependencies=[Security(verify_api_key)],
        summary="Liste des stations.",
        description="Informations sur les stations."
)
async def get_stations():
    return stations_data

"""
@app.get(
        "/api/validations",
          dependencies=[Security(verify_api_key)],
)
async def get_validations():
    return validations_data
"""


# Endpoint pour récupérer les données de toutes les lignes.
@app.get(
        "/api/validations/ligne", 
        dependencies=[Security(verify_api_key)],
        summary="Validations pour toutes les lignes",
        description="Récupérer les validations pour toutes les lignes de transport."
)
async def get_validations_ligne():
    return validations_ligne_data


# Endpoint pour récupérer les données d'une ligne spécifique.
@app.get(
        "/api/validations/ligne/{Ligne}", 
        dependencies=[Security(verify_api_key)],
        summary="Validations pour une ligne spécifique.",
        description="Récupérer les validations pour une ligne donnée."
)
async def get_validations_une_ligne(Ligne: str):
    for ligne in validations_ligne_data:
        if ligne.get("Ligne") == Ligne:
            return ligne
    raise HTTPException(status_code=404, detail="Ligne introuvable")
