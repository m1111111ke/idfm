# Stockage des données dans une base de données SQLite.

# Imports
import sqlite3
import pandas as pd
import os

# Fonction création et connexion à la base de données.

def create_database_connection():

    # Chemin du répertoire pour la base de donnée.
    db_folder_path = os.path.join("..", "data", "database")

    # Vérifier et créer le répertoire de destination s'il n'existe pas.
    if not os.path.exists(db_folder_path):
        os.makedirs(db_folder_path)
    
    db_path = os.path.join("..", "data", "database", "idfm.db")
    return sqlite3.connect(db_path)


# Fonction pour créer les tables et importer les données vers la base.

def insert_data_from_csv(csv_file, table_name, conn):
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

def main():
    # Créer une connexion à la base de données.
    conn = create_database_connection()
    
    try:
        # Insérer les données dans les tables.
        insert_data_from_csv(os.path.join('..', 'data', 'processed', 'stations.csv'), "stations", conn)
        insert_data_from_csv(os.path.join('..', 'data', 'processed', 'validations.csv'), "validations", conn)
        insert_data_from_csv(os.path.join('..', 'data', 'processed', 'validations_ligne.csv'), "validations_ligne", conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # S'assurer que la connexion est fermée.
        conn.close()

if __name__ == "__main__":
    main()
