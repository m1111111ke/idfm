# IDFM — Analyse des données de validation de titres de transport

Projet de data science analysant les données ouvertes d'Île-de-France Mobilités (IDFM) sur les **validations de titres de transport** du réseau ferré francilien (métro, RER, train). Le projet couvre l'ensemble de la chaîne : collecte des données, préparation/agrégation, stockage, exposition via une API sécurisée, et restitution via un dashboard interactif.

## Sommaire

- [Contexte](#contexte)
- [Sources de données](#sources-de-données)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API](#api)
- [Dashboard](#dashboard)
- [Documentation](#documentation)
- [Tests](#tests)
- [Stack technique](#stack-technique)

## Contexte

Les données proviennent du système de collecte et de partage de la Plateforme Régionale d'Information pour la Mobilité (PRIM) d'Île-de-France Mobilités, issu de l'usage des passes Navigo. Elles permettent d'analyser les flux de voyageurs sur le réseau ferré (les validations y sont rattachées à une station, contrairement au réseau de surface — bus, tram — où la validation se fait dans le véhicule). Ces chiffres sont mis à jour semestriellement et offrent une vision partielle du trafic (hors tickets magnétiques, forfaits spéciaux et fraude).

Le projet explore notamment :
- la répartition des validations par jour de la semaine et par mois,
- les stations avec le plus et le moins de validations,
- une carte interactive des stations,
- la répartition par catégorie de titre de transport (Navigo, Imagine R, Améthyste, etc.),
- les validations agrégées par ligne,
- une corrélation entre la proximité des écoles et l'usage du forfait Imagine R,
- une corrélation entre le nombre de lignes desservant une station et son volume de validations.

## Sources de données

Données ouvertes récupérées automatiquement depuis :
- **data.iledefrance-mobilites.fr** : validations de titres par trimestre (réseau ferré) et emplacement des gares/stations.
- **data.iledefrance.fr** : liste et localisation des établissements scolaires (1er et 2d degrés) en Île-de-France.

## Structure du projet

```
├── api/                     # API FastAPI pour servir les données traitées
│   └── main.py
├── src/                     # Scripts du pipeline de données
│   ├── collecte.py          # Téléchargement des sources (validations, stations, écoles)
│   ├── preparation.py       # Nettoyage, fusion et agrégation des données
│   ├── stockage.py          # Chargement des données dans une base SQLite
│   └── app.py                # Dashboard Streamlit d'analyse et de visualisation
├── notebooks/               # Notebooks Jupyter d'exploration et d'analyse
│   ├── 1_idfm.ipynb
│   ├── 2_idfm_analyses.ipynb
│   ├── 3_idfm_db.ipynb
│   └── 4_idfm_geopandas.ipynb
├── config/                  # Fichiers de configuration
├── docs/                    # Documentation (MkDocs)
├── tests/                   # Tests unitaires et d'intégration
├── requirements.txt         # Dépendances du projet
├── Makefile                 # Commandes de développement
└── mkdocs.yaml
```

## Installation

Prérequis : Python 3.11.

```bash
git clone https://github.com/m1111111ke/idfm.git
cd idfm

# Créer un environnement virtuel et installer les dépendances
make setup

# Installer les hooks pre-commit
make install_precommit
```

Ou manuellement :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

Le pipeline de données s'exécute en trois étapes, depuis le dossier `src/` :

```bash
cd src

# 1. Télécharger les fichiers sources (validations, stations, écoles)
python collecte.py

# 2. Nettoyer, fusionner et agréger les données
python preparation.py

# 3. Charger les données dans une base SQLite locale (data/database/idfm.db)
python stockage.py
```

## API

Une API FastAPI sécurisée par clé permet de servir les données traitées (stations et validations par station/par ligne).

```bash
cd api
uvicorn main:app --reload
```

Endpoints principaux (authentification via l'en-tête `X-API-Key`) :

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/` | Message de bienvenue |
| GET | `/health` | Statut de l'API |
| GET | `/api/stations` | Liste des stations |
| POST | `/api/stations` | Créer une nouvelle station |
| GET | `/api/validations_station` | Validations pour toutes les stations |
| GET | `/api/validations_station/{id_zdc}` | Validations pour une station donnée |
| GET | `/api/validations/ligne` | Validations pour toutes les lignes |
| GET | `/api/validations/ligne/{Ligne}` | Validations pour une ligne donnée |
| POST | `/api/validations/ligne` | Créer une nouvelle ligne |

La documentation interactive Swagger est disponible sur `/docs` une fois l'API lancée.

## Dashboard

Un dashboard Streamlit permet d'explorer visuellement les données (graphiques, carte des stations, corrélations) :

```bash
cd src
streamlit run app.py
```

## Documentation

La documentation du projet est générée avec MkDocs (thème Material).

```bash
# Servir la documentation en local sur http://localhost:8001
make serve_docs_locally

# Déployer sur GitHub Pages
make deploy_docs
```

## Tests

```bash
make run_tests
```

## Stack technique

- **Données & traitement** : pandas, geopandas
- **Visualisation** : plotly, matplotlib, seaborn, Streamlit
- **API** : FastAPI, Pydantic
- **Stockage** : SQLite
- **Qualité de code** : pre-commit, Ruff, Bandit
- **Documentation** : MkDocs Material
- **Tests** : Pytest

## Licence

Ce projet est sous licence MIT — voir le fichier LICENSE pour plus de détails.
