# Collecte des données.

# Imports

import os
import requests

# 1. Télécharger les fichiers sources depuis la Plateforme Régionale d'Information pour la Mobilité (PRIM) d'Ile-de-France Mobilités et enregistrer localement.

# Données de validation de titres par trimestre.

url_validations_t1 = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-1er-trimestre/exports/csv"

url_validations_t2 = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/exports/csv"

url_validations_t3 = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-3eme-trimestre/exports/csv"

url_validations_t4 = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-4eme-trimestre/exports/csv"


# Chemin du répertoire pour mettre les fichiers csv de validation.
folder_path_validations_multiples = os.path.join(
    "..", "data", "raw", "validations_multiples"
)

# Vérifier et créer le répertoire de destination s'il n'existe pas.

if not os.path.exists(folder_path_validations_multiples):
    os.makedirs(folder_path_validations_multiples)
    print(f"Répertoire créé : {folder_path_validations_multiples}")


# 2. Liste et emplacements des gares / stations.

url_stations = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/emplacement-des-gares-idf-data-generalisee/exports/csv"


# Chemin du répertoire pour mettre les fichiers csv de liste et emplacement des gares / stations.
folder_path_stations = os.path.join("..", "data", "raw", "stations")

# Vérifier et créer le répertoire de destination s'il n'existe pas.

if not os.path.exists(folder_path_stations):
    os.makedirs(folder_path_stations)
    print(f"Répertoire créé : {folder_path_stations}")


# 3. Télécharger le fichier source de la liste des écoles (maternelles, primaires, collèges et lycées) et leur localisation en Ile-de-France depuis "Région Ile-de-France Open data."

# Objectif : compter le nombre d'écoles à proximité de chaque station et voir si cela influe le nombre de validations de titres Imagine R.

url_ecoles = "https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/les_etablissements_d_enseignement_des_1er_et_2d_degres_en_idf/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"

# Chemin du répertoire pour mettre le fichier csv d'emplacement des écoles.
folder_path_ecoles = os.path.join("..", "data", "raw")

# Vérifier et créer le répertoire de destination s'il n'existe pas.

if not os.path.exists(folder_path_ecoles):
    os.makedirs(folder_path_ecoles)
    print(f"Répertoire créé : {folder_path_ecoles}")


# Définir une fonction pour télécharger les sources.


def telecharger_csv(url, destination, fichier):
    # Chemin complet du fichier.
    filepath = os.path.join(destination, fichier)
    try:
        print(f"Téléchargement en cours depuis : {url}")

        # Effectuer une requête HTTP.
        reponse = requests.get(url, timeout=10)

        # Erreur si le statut HTTP n'est pas bon (404, 500).
        reponse.raise_for_status()

        # Ecrire le contenu dans un fichier (en mode binaire).
        with open(filepath, "wb") as f:
            f.write(reponse.content)

        print(f"Fichier enregistré sous : {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")


if __name__ == "__main__":
    # Télécharger les fichiers de validations.

    url = url_validations_t1
    destination = folder_path_validations_multiples
    fichier = "validations_t1.csv"

    telecharger_csv(url, destination, fichier)

    url = url_validations_t2
    destination = folder_path_validations_multiples
    fichier = "validations_t2.csv"

    telecharger_csv(url, destination, fichier)

    url = url_validations_t3
    destination = folder_path_validations_multiples
    fichier = "validations_t3.csv"

    telecharger_csv(url, destination, fichier)

    url = url_validations_t4
    destination = folder_path_validations_multiples
    fichier = "validations_t4.csv"

    telecharger_csv(url, destination, fichier)

    # Télécharger les fichiers de liste et emplacements des gares / stations.

    url = url_stations
    destination = folder_path_stations
    fichier = "stations.csv"

    telecharger_csv(url, destination, fichier)

    # Télécharger le fichier des emplacements des écoles.

    url = url_ecoles
    destination = folder_path_ecoles
    fichier = "ecoles.csv"

    telecharger_csv(url, destination, fichier)
