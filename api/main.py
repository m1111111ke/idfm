# Mise à disposition des données via une API.

# Imports
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
from pydantic import BaseModel

# Configuration des logs.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gestion des chemins.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data" / "processed"

# Stockage global des données (sous forme de dictionnaires pour un accès rapide)
stations_list = []
validations_station_dict = {}
validations_ligne_dict = {}


# Gestion du cycle de vie (Lifespan).
@asynccontextmanager
async def lifespan(app: FastAPI):
    global stations_list, validations_station_dict, validations_ligne_dict
    logger.info("Chargement et traitement des fichiers CSV en cours...")

    try:
        # 1. Stations.
        colonnes_stations = [
            "id_ref_zdc",
            "nom_zdc",
            "res_com",
            "mode",
            "nb_lignes",
            "latitude",
            "longitude",
        ]
        stations_list = pd.read_csv(
            DATA_DIR / "stations.csv", usecols=colonnes_stations
        ).to_dict(orient="records")

        # 2. Validations par station.
        colonnes_validations_station = ["id_zdc", "nom_zdc", "nb_vald"]
        df_val_station = (
            pd.read_csv(
                DATA_DIR / "validations_fusion.csv",
                usecols=colonnes_validations_station,
            )
            .groupby(["id_zdc", "nom_zdc"])["nb_vald"]
            .sum()
            .reset_index()
        )
        # Indexation par id_zdc converti en string pour faciliter la recherche directe.
        validations_station_dict = df_val_station.set_index("id_zdc").to_dict(
            orient="index"
        )

        # 3. Validations par ligne
        df_ligne = pd.read_csv(DATA_DIR / "validations_ligne.csv")
        # Stockage en minuscules pour une recherche insensible à la casse.
        validations_ligne_dict = {
            str(k).lower(): v
            for k, v in df_ligne.set_index("Ligne").to_dict(orient="index").items()
        }

        logger.info("Données chargées et converties avec succès !")
    except FileNotFoundError as e:
        logger.error(f"Impossible de trouver les fichiers de données : {e}")
        raise e

    yield
    logger.info("Fermeture de l'application.")


# Initialisation de FastAPI avec le lifespan.
app = FastAPI(
    title="API Données de Validations de Titre de Transports",
    description="Une API sécurisée par clé pour servir les données de validations de titre de transport en Ile-de-France et de stations/gares.",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API des données de validation de titre de transport en Ile-de-France !"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Data API"}


#   SECURITE.
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("MY_API_KEY", "ma_cle_secrete_123")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide ou manquante.",
        )
    return api_key


# Modèle Pydantic pour station.
class StationCreate(BaseModel):
    id_ref_zdc: str
    nom_zdc: str
    res_com: str
    mode: str
    nb_lignes: int
    latitude: float
    longitude: float


# Modèle Pydantic pour ligne.
class LigneCreate(BaseModel):
    Ligne: str  # Exemple: "METRO 17"
    nb_vald: int  # Exemple: 1250000


# ENDPOINTS.


# Endpoint GET liste des stations.
@app.get(
    "/api/stations",
    dependencies=[Security(verify_api_key)],
    summary="Liste des stations.",
    description="Informations sur les stations.",
)
async def get_stations():
    return stations_list


# Endpoint POST nouvelle station.
@app.post(
    "/api/stations",
    dependencies=[Security(verify_api_key)],
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle station.",
    description="Ajoute une nouvelle station à la liste en mémoire.",
)
async def create_station(station: StationCreate):
    global stations_list

    # Vérifier si l'ID de la station existe déjà pour éviter les doublons.
    for s in stations_list:
        if s.get("id_ref_zdc") == station.id_ref_zdc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Une station avec l'ID {station.id_ref_zdc} existe déjà.",
            )

    # Convertir le modèle Pydantic en dictionnaire Python.
    nouvelle_station = (
        station.model_dump()
    )  # Utilise station.dict() si tu as une vieille version de Pydantic.

    # Ajouter la station à la liste globale.
    stations_list.append(nouvelle_station)

    logger.info(
        f"Nouvelle station créée : {nouvelle_station['nom_zdc']} (ID: {nouvelle_station['id_ref_zdc']})"
    )

    # Retourner la station créée au client.
    return nouvelle_station


# Endpoint GET pour validations par station.
@app.get(
    "/api/validations_station",
    dependencies=[Security(verify_api_key)],
    summary="Validations de titre pour toutes les stations",
    description="Récupérer les données de validation de titre pour toutes les stations.",
)
async def get_validations():
    # convertit le dictionnaire interne en liste pour l'output de l'API. List comprehension parcourt le dictionnaire, récupère la clé k et la valeur v.
    return [{"id_zdc": k, **v} for k, v in validations_station_dict.items()]


# Endpoint GET pour validation pour une station spécifique.
@app.get(
    "/api/validations_station/{id_zdc}",
    dependencies=[Security(verify_api_key)],
    summary="Validations de titre pour une station spécifique.",
    description="Récupérer les données de validation de titre pour une station donnée via son id (ex: Châtelet-les-Halles : 474151).",
)
async def get_validations_une_station(id_zdc: str):
    # Recherche ultra rapide en O(1) avec sécurité en convertissant la clé en entier.
    station = validations_station_dict.get(id_zdc) or validations_station_dict.get(
        int(id_zdc) if id_zdc.isdigit() else None
    )

    if station:
        return {"id_zdc": id_zdc, **station}
    raise HTTPException(status_code=404, detail="Station introuvable")


# Endpoint GET validations par ligne.
@app.get(
    "/api/validations/ligne",
    dependencies=[Security(verify_api_key)],
    summary="Validations de titre pour toutes les lignes",
    description="Récupérer les données de validation de titre pour toutes les lignes de transport.",
)
async def get_validations_ligne():
    # Convertit le dictionnaire interne des lignes en liste pour afficher au format JSON.
    return [{"Ligne": k, **v} for k, v in validations_ligne_dict.items()]


# Endpoint GET validation pour une ligne spécifique.
@app.get(
    "/api/validations/ligne/{Ligne}",
    dependencies=[Security(verify_api_key)],
    summary="Validations de titre pour une ligne spécifique.",
    description="Récupérer les données de validation de titre pour une ligne donnée (ex: RER A, METRO 1).",
)
async def get_validations_une_ligne(Ligne: str):
    # Recherche en O(1) insensible à la casse
    ligne_data = validations_ligne_dict.get(Ligne.lower())
    if ligne_data:
        return {"Ligne": Ligne, **ligne_data}
    raise HTTPException(status_code=404, detail="Ligne introuvable")


# Endpoint POST pour créer une nouvelle ligne.
@app.post(
    "/api/validations/ligne",
    dependencies=[Security(verify_api_key)],
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle ligne de transport.",
    description="Ajoute une nouvelle ligne avec ses données de validation dans le dictionnaire en mémoire.",
)
async def create_ligne(ligne: LigneCreate):
    global validations_ligne_dict

    # Normaliser le nom de la ligne en minuscules pour la clé du dictionnaire.
    cle_ligne = ligne.Ligne.lower()

    # Vérifier si la ligne existe déjà (insensible à la casse).
    if cle_ligne in validations_ligne_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La ligne '{ligne.Ligne}' existe déjà.",
        )

    # Convertir le modèle Pydantic en dictionnaire.
    donnees_ligne = ligne.model_dump()

    # Extraire le nom de la ligne pour s'en servir de clé,
    # et stocker le reste des données dans le dictionnaire global.
    nom_original = donnees_ligne.pop("Ligne")
    validations_ligne_dict[cle_ligne] = donnees_ligne

    logger.info(f"Nouvelle ligne créée avec succès : {nom_original}")

    # Retourner un aperçu de ce qui a été enregistré.
    return {"Ligne": nom_original, **donnees_ligne}
