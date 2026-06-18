# Préparation des données et agrégation.

# Imports

import os
import glob
import pandas as pd


# 1. Données de validation de titres.


# Objectif : combiner les fichiers sources de validations en un seul fichier csv.

# Corriger nom de colonne "ida" pour "validations_t1.csv" alors que les autres csv sont en "id_zdc"
filepath_t1 = os.path.join(
    "..", "data", "raw", "validations_multiples", "validations_t1.csv"
)
df_t1 = pd.read_csv(filepath_t1, sep=";")

# Correction nom de colonne "ida" en "id_zdc"
df_t1 = df_t1.rename(columns={"ida": "id_zdc"})

# Enregistrer en csv
filepath_validations_multiples = os.path.join(
    "..", "data", "raw", "validations_multiples", "validations_t1.csv"
)
df_t1.to_csv(filepath_validations_multiples, sep=";", index=False, encoding="utf-8-sig")


# 4 fichiers csv de validations de titres (1 par trimestre) pour l'année à combiner

# Chemin du répertoire où se trouvent les fichiers csv à combiner
folder_path_validations_multiples = os.path.join(
    "..", "data", "raw", "validations_multiples"
)

# Récuperer tous les fichiers csv dans ce répertoire
validations = glob.glob(os.path.join(folder_path_validations_multiples, "*.csv"))

# List comprehension pour lire et combiner / concaténer
validations_df = pd.concat(
    (pd.read_csv(f, sep=";") for f in validations), ignore_index=True
)

# Chemin du répertoire pour mettre le fichiers csv de validation combiné.
folder_path_validations = os.path.join("..", "data", "raw", "validations")

# Vérifier et créer le répertoire de destination s'il n'existe pas.
if not os.path.exists(folder_path_validations):
    os.makedirs(folder_path_validations)
    print(f"Répertoire créé : {folder_path_validations}")

# Exporter vers un fichier csv.
combined_validations_filepath = os.path.join(
    "..", "data", "raw", "validations", "validations.csv"
)
validations_df.to_csv(combined_validations_filepath, index=False)

print(
    f"Les {len(validations)} fichiers csv sont combinés avec succès dans : {combined_validations_filepath} !"
)


# Formater colonne "jour".
validations_df["jour"] = pd.to_datetime(validations_df["jour"])

# Ajout colonnes mois.
validations_df["mois"] = validations_df["jour"].dt.month

# Ajout colonnes jour de la semaine (0 pour Lundi et 6 pour Dimanche).
validations_df["jour_sem_num"] = validations_df["jour"].dt.weekday

# Correction "categorie_titre": renommer "Contrat Solidarité Transport" par "Contrat Solidarite Transport"
validations_df["categorie_titre"] = validations_df["categorie_titre"].replace(
    "Contrat Solidarité Transport", "Contrat Solidarite Transport"
)

# Attribuer une "id_zdc" à "Aéroport d'Orly" (information depuis la table stations)
validations_df.loc[validations_df["libelle_arret"] == "Aéroport d'Orly", "id_zdc"] = (
    63284
)

# Supprimer les lignes dont "libelle_arret" == "Inconnu" (séléctionner les lignes où le libellé est différent de "Inconnu" et écraser l'acien dataframe).
validations_df = validations_df[validations_df["libelle_arret"] != "Inconnu"]

# Modifier id_zdc de float64 en int64.
validations_df["id_zdc"] = validations_df["id_zdc"].astype(int)

# Modifier id_zdc de int64 en str.
validations_df["id_zdc"] = validations_df["id_zdc"].astype(str)

# Correction "id_zdc" de validations pour correspondre aux "id_ref_zdc" des stations.

dictionnaire_id_zdc = {
    "59577": "478855",
    "62737": "478505",
    "63650": "463850",
    "67747": "462934",
    "69531": "463754",
    "71219": "473829",
    "71245": "71229",
    "71282": "479068",
    "71686": "71697",
    "71743": "463564",
    "72059": "478883",
    "72219": "72225",
    "73616": "478885",
    "73792": "478926",
    "73794": "474151",
    "73795": "474152",
    "74040": "71139",
    "74371": "463843",
    "93066": "490784",
    "412697": "479919",
    "425819": "66915",
    "474149": "73615",
    "474150": "71229",
    "482368": "73688",
    "492980": "71271",
}

validations_df["id_zdc"] = validations_df["id_zdc"].replace(dictionnaire_id_zdc)

# Modifier id_zdc Magenta par 478733
validations_df.loc[
    (validations_df["id_zdc"] == "74000")
    & (validations_df["libelle_arret"] == "MAGENTA"),
    "id_zdc",
] = "478733"

# Modifier id_zdc La Chapelle par 71434
validations_df.loc[
    (validations_df["id_zdc"] == "74000")
    & (validations_df["libelle_arret"] == "LA CHAPELLE"),
    "id_zdc",
] = "71434"


# 2. Liste et emplacement des gares / stations.


# Liste des stations généralisée (une station peut regrouper plusieurs lignes de transport associées)
filepath_stations = os.path.join("..", "data", "raw", "stations", "stations.csv")
stations_df = pd.read_csv(filepath_stations, sep=";")

# Création Colonnes latitude et longitude.
stations_df[["latitude", "longitude"]] = (
    stations_df["geo_point_2d"].str.split(", ", expand=True).astype(float)
)

# Modifier id_zdc en str.
stations_df["id_ref_zdc"] = stations_df["id_ref_zdc"].astype(str)

# Remplacer dans "termetro": "METRO 14" par 1 (valeur 1 ou 0 uniquement).
stations_df.loc[stations_df["termetro"] == "METRO 14", "termetro"] = 1

# Modifier termetro de object à int64.
stations_df["termetro"] = stations_df["termetro"].astype(int)

# Correction de noms de stations et res_com.

stations_df.loc[stations_df["id_ref_zdc"] == "478733", "nom_zdc"] = "Magenta"
stations_df.loc[stations_df["id_ref_zdc"] == "478855", "nom_zdc"] = "Etampes"
stations_df.loc[stations_df["id_ref_zdc"] == "71697", "nom_zdc"] = "Avron"
stations_df.loc[stations_df["id_ref_zdc"] == "479928", "nom_zdc"] = "Buzenval"
stations_df.loc[stations_df["id_ref_zdc"] == "73688", "nom_zdc"] = "Havre-Caumartin"


stations_df.loc[stations_df["id_ref_zdc"] == "71697", "res_com"] = "METRO 9"
stations_df.loc[stations_df["id_ref_zdc"] == "479928", "res_com"] = "METRO 2"
stations_df.loc[stations_df["id_ref_zdc"] == "73688", "res_com"] = "METRO 3 / METRO 9"


# Correction Châtelet les Halles.

stations_df.loc[
    (stations_df["id_ref_zdc"] == "474151")
    & (stations_df["nom_zdc"] == "Châtelet les Halles"),
    "res_com",
] = "RER A / RER B / RER D / METRO 4"
stations_df.loc[
    (stations_df["id_ref_zdc"] == "474151")
    & (stations_df["nom_zdc"] == "Châtelet les Halles"),
    "mode",
] = "RER / METRO"
stations_df.loc[
    (stations_df["id_ref_zdc"] == "474151")
    & (stations_df["nom_zdc"] == "Châtelet les Halles"),
    "metro",
] = 1
stations_df["metro"] = stations_df["metro"].astype(int)

# Modifier id_ref_zdc Château Landon par 73615
stations_df.loc[
    (stations_df["id_ref_zdc"] == "71359")
    & (stations_df["nom_zdc"] == "Château Landon"),
    "id_ref_zdc",
] = "73615"

# Suppression des doublons id_ref_zdc

stations_df = stations_df[
    ~(
        (stations_df["id_ref_zdc"] == "63284")
        & (stations_df["nom_zdc"] == "Aéroport Orly 1-2-3 (Terminal Ouest)")
    )
]
stations_df = stations_df[
    ~(
        (stations_df["id_ref_zdc"] == "69677")
        & (stations_df["nom_zdc"] == "Pont de Rungis Aéroport d'Orly")
    )
]
stations_df = stations_df[
    ~((stations_df["id_ref_zdc"] == "71229") & (stations_df["nom_zdc"] == "La Muette"))
]
stations_df = stations_df[
    ~(
        (stations_df["id_ref_zdc"] == "71607")
        & (stations_df["nom_zdc"] == "Gare de Bercy")
    )
]
stations_df = stations_df[
    ~(
        (stations_df["id_ref_zdc"] == "73620")
        & (stations_df["nom_zdc"] == "Cluny La Sorbonne")
    )
]
stations_df = stations_df[
    ~(
        (stations_df["id_ref_zdc"] == "73753")
        & (stations_df["nom_zdc"] == "Porte de Thiais (Marché international)")
    )
]
stations_df = stations_df[
    ~(
        (stations_df["id_ref_zdc"] == "474151")
        & (stations_df["nom_zdc"] == "Les Halles")
    )
]

# Ajout colonne "nb_lignes" nombre de ligne selon contenu de "res_com".
stations_df["nb_lignes"] = stations_df["res_com"].str.count("/") + 1


# 3. Merge - agrégation.


# Merge.
df = validations_df.merge(
    stations_df, how="left", left_on="id_zdc", right_on="id_ref_zdc"
)

# Supprimer les colonnes non utiles.
colonnes_a_supprimer = [
    "code_stif_trns",
    "code_stif_res",
    "code_stif_arret",
    "nom_long",
    "nom_so_gar",
    "nom_su_gar",
    "geo_point_2d",
    "geo_shape",
    "objectid_1",
    "codeunique",
    "id_ref_zda",
    "nom_zda",
    "idrefliga",
    "idrefligc",
    "x",
    "y",
]

df = df.drop(columns=colonnes_a_supprimer)

# Modifier "nb_vald" de float64 en int64.
df["nb_vald"] = df["nb_vald"].astype(int)


# 4. Table Nombre de validations par lignes de transport.


# List comprehension pour calculer le nombre de validations par lignes de transport.

lignes = [
    "RER A",
    "RER B",
    "RER C",
    "RER D",
    "RER E",
    "METRO 1",
    "METRO 2",
    "METRO 3",
    "METRO 3bis",
    "METRO 4",
    "METRO 5",
    "METRO 6",
    "METRO 7",
    "METRO 7bis",
    "METRO 8",
    "METRO 9",
    "METRO 10",
    "METRO 11",
    "METRO 12",
    "METRO 13",
    "METRO 14",
    "TRAIN H",
    "TRAIN J",
    "TRAIN K",
    "TRAIN L",
    "TRAIN N",
    "TRAIN P",
    "TRAIN R",
    "TRAIN V",
    "TRAM 1",
    "TRAM 2",
    "TRAM 3",
    "TRAM 3a",
    "TRAM 3b",
    "TRAM 4",
    "TRAM 5",
    "TRAM 6",
    "TRAM 7",
    "TRAM 8",
    "TRAM 9",
    "TRAM 10",
    "TRAM 11",
    "TRAM 12",
    "TRAM 13",
    "TRAM 14",
    "CABLE 1",
    "CDGVAL",
    "FUNICULAIRE MONTMARTRE",
]

lignes_df = pd.DataFrame(
    {
        "Ligne": lignes,
        "somme_nb_vald": [
            df[df["res_com"].str.contains(ligne, na=False)]["nb_vald"].sum()
            for ligne in lignes
        ],
    }
)


# 5. Exportation vers csv.


# 5.1. Sauvegarder les données de validations traitées dans un nouveau csv.

processed_validations_filepath = os.path.join(
    "..", "data", "processed", "validations.csv"
)
validations_df.to_csv(processed_validations_filepath, index=False, encoding="utf-8-sig")

print(
    f"Fichier 'données de validations' traité enregistré sous : {processed_validations_filepath}"
)


# 5.2. Sauvegarder les données de stations traitées dans un nouveau csv.

processed_stations_filepath = os.path.join("..", "data", "processed", "stations.csv")
stations_df.to_csv(processed_stations_filepath, index=False, encoding="utf-8-sig")

print(
    f"Fichier 'liste des stations' traité enregistré sous : {processed_stations_filepath}"
)


# 5.3. Sauvegarder les données fusionnées dans un nouveau csv.

processed_fusion_filepath = os.path.join(
    "..", "data", "processed", "validations_fusion.csv"
)
df.to_csv(processed_fusion_filepath, index=False, encoding="utf-8-sig")

print(
    f"Fichier 'fusion validations et stations' enregistré sous : {processed_fusion_filepath}"
)


# 5.4. Sauvegarder les données de validations par ligne de transport dans un nouveau csv.

processed_ligne_filepath = os.path.join(
    "..", "data", "processed", "validations_ligne.csv"
)
lignes_df.to_csv(processed_ligne_filepath, index=False, encoding="utf-8-sig")

print(f"Fichier 'validations par ligne' enregistré sous : {processed_ligne_filepath}")
