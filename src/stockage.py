# Stockage des données dans une base de données SQLite.

# Imports

import sqlite3
import pandas as pd
import os



# 1. Création de la base de données SQLite.

# Chemin du répertoire pour la base de donnée.
db_folder_path = os.path.join("..","data","database")

# Vérifier et créer le répertoire de destination s'il n'existe pas.
if not os.path.exists(db_folder_path):
    os.makedirs(db_folder_path)

db_path = os.path.join("..","data","database","idfm.db")

conn = sqlite3.connect(db_path)

cur = conn.cursor()



# 2. Création des tables.


# 2.1. Table des stations.

# Lire le csv
processed_stations_filepath = os.path.join('..','data','processed','stations.csv')
stations_df = pd.read_csv(processed_stations_filepath)

# Connexion à la base SQLite
conn = sqlite3.connect(db_path)

# Importer dans une table.
stations_df.to_sql(
    "stations",
    conn,
    if_exists="replace",
    index=False
)

conn.close()


# 2.2. Table de validations.

# Lire le csv
processed_validations_filepath = os.path.join('..','data','processed','validations.csv')
validations_df = pd.read_csv(processed_validations_filepath)

# Connexion à la base SQLite
conn = sqlite3.connect(db_path)

# Importer dans une table.
validations_df.to_sql(
    "validations",
    conn,
    if_exists="replace",
    index=False
)

conn.close()


# 2.3. Table de validations par ligne.

# Lire le csv
processed_validations_ligne_filepath = os.path.join('..','data','processed','validations_ligne.csv')
validations_ligne_df = pd.read_csv(processed_validations_ligne_filepath)

# Connexion à la base SQLite
conn = sqlite3.connect(db_path)

# Importer dans une table.
validations_ligne_df.to_sql(
    "validations_ligne",
    conn,
    if_exists="replace",
    index=False
)

conn.close()