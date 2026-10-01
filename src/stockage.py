# Stockage des données dans une base de données SQLite.

# Imports
import os
import sqlite3

import pandas as pd

print("Stockage des données dans une base de données SQLite 3.")

# 1. DDL : schéma de la base (clés primaires et étrangères).
# Les tables sont listées dans l'ordre de création.

DDL = {
    "stations": """
        CREATE TABLE stations (
            geo_point_2d TEXT,
            geo_shape    TEXT,
            objectid_1   INTEGER,
            codeunique   INTEGER,
            nom_long     TEXT,
            nom_so_gar   TEXT,
            nom_su_gar   TEXT,
            id_ref_zdc   INTEGER PRIMARY KEY,
            nom_zdc      TEXT,
            id_ref_zda   INTEGER,
            nom_zda      TEXT,
            idrefliga    TEXT,
            idrefligc    TEXT,
            res_com      TEXT,
            mode         TEXT,
            train        INTEGER,
            rer          INTEGER,
            metro        INTEGER,
            tramway      INTEGER,
            val          INTEGER,
            tertrain     INTEGER,
            terrer       INTEGER,
            termetro     INTEGER,
            tertram      INTEGER,
            terval       INTEGER,
            exploitant   TEXT,
            idf          INTEGER,
            principal    INTEGER,
            x            REAL,
            y            REAL,
            latitude     REAL,
            longitude    REAL,
            nb_lignes    INTEGER,
            nb_ecoles    INTEGER
        )
    """,
    "validations": """
    CREATE TABLE validations (
        id_validation   INTEGER PRIMARY KEY AUTOINCREMENT,
        jour            TEXT    NOT NULL,
        code_stif_trns  REAL,
        code_stif_res   INTEGER,
        code_stif_arret INTEGER,
        libelle_arret   TEXT,
        id_zdc          INTEGER,
        categorie_titre TEXT,
        nb_vald         REAL,
        mois            INTEGER,
        jour_sem_num    INTEGER,
        FOREIGN KEY (id_zdc) REFERENCES stations (id_ref_zdc)
    )
""",
    "validations_fusion": """
        CREATE TABLE validations_fusion (
            jour            TEXT,
            libelle_arret   TEXT,
            id_zdc          INTEGER,
            categorie_titre TEXT,
            nb_vald         REAL,
            mois            INTEGER,
            jour_sem_num    INTEGER,
            id_ref_zdc      INTEGER,
            nom_zdc         TEXT,
            res_com         TEXT,
            mode            TEXT,
            train           INTEGER,
            rer             INTEGER,
            metro           INTEGER,
            tramway         INTEGER,
            val             INTEGER,
            tertrain        INTEGER,
            terrer          INTEGER,
            termetro        INTEGER,
            tertram         INTEGER,
            terval          INTEGER,
            exploitant      TEXT,
            idf             INTEGER,
            principal       INTEGER,
            latitude        REAL,
            longitude       REAL,
            nb_lignes       INTEGER,
            nb_ecoles       INTEGER,
            FOREIGN KEY (id_ref_zdc) REFERENCES stations (id_ref_zdc)
        )
    """,
    "validations_ligne": """
        CREATE TABLE validations_ligne (
            Ligne         TEXT PRIMARY KEY,
            somme_nb_vald REAL
        )
    """,
}

# Fichiers sources (table -> chemin du csv).
PROCESSED = os.path.join("..", "data", "processed")
CSV_FILES = {
    "stations": os.path.join(PROCESSED, "stations.csv"),
    "validations": os.path.join(PROCESSED, "validations.csv"),
    "validations_fusion": os.path.join(PROCESSED, "validations_fusion.csv"),
    "validations_ligne": os.path.join(PROCESSED, "validations_ligne.csv"),
}

# 2. Connexion.


def create_database_connection():
    db_folder_path = os.path.join("..", "data", "database")
    os.makedirs(db_folder_path, exist_ok=True)
    db_path = os.path.join(db_folder_path, "idfm.db")
    conn = sqlite3.connect(db_path)
    # Active le contrôle des clés étrangères (désactivé par défaut dans SQLite).
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# 3. Création du schéma.


def create_tables(conn):
    # Suppression en ordre inverse (enfants avant parents) pour respecter les FK.
    for table in reversed(list(DDL)):
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    for table, ddl in DDL.items():
        conn.execute(ddl)
    conn.commit()


# 4. Chargement des données.


def insert_data_from_csv(csv_file, table_name, conn):
    df = pd.read_csv(csv_file)
    # "append" (et non "replace") pour conserver les contraintes du DDL.
    df.to_sql(table_name, conn, if_exists="append", index=False)


def check_foreign_keys(conn):
    # Signale les lignes orphelines (ex. id_zdc sans station correspondante).
    orphans = conn.execute("PRAGMA foreign_key_check").fetchall()
    if orphans:
        print(f"Attention : {len(orphans)} ligne(s) violent une clé étrangère.")
    else:
        print("Contrôle des clés étrangères : OK.")


def main():
    conn = create_database_connection()
    try:
        print("Création des tables avec contraintes...")
        create_tables(conn)

        # Ordre de chargement : stations d'abord (table parente).
        # Pendant le chargement, on désactive le contrôle des FK : les écarts
        # éventuels sont rapportés ensuite par check_foreign_keys().
        conn.execute("PRAGMA foreign_keys = OFF")
        for table, csv_file in CSV_FILES.items():
            print(f"Insertion des données de {table}...")
            insert_data_from_csv(csv_file, table, conn)
            print(f"Insertion des données de {table} terminée !")
        conn.commit()

        conn.execute("PRAGMA foreign_keys = ON")
        check_foreign_keys(conn)
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
