# Streamlit

import streamlit as st
import os
import pandas as pd
import plotly.express as px

st.image(
    "https://upload.wikimedia.org/wikipedia/fr/c/ce/IdFMobilit%C3%A9s.svg", width=300
)

st.title(
    "Ile-de-France Mobilités : Analyse de données de validation de titres de transport."
)
st.write(
    "Sources : Plateforme Régionale d'Information pour la Mobilité (PRIM) d'Ile-de-France Mobilités."
)

st.write(
    "Ces données proviennent du système de collecte et de partage des données de validation du réseau de transport en Île-de-France : de l'usage des passes Navigo, permettant à Île-de-France Mobilités d'analyser les flux de voyageurs tout en garantissant un anonymat strict validé par la CNIL."
)

st.write(
    "Ces statistiques, actualisées semestriellement, sont accessibles en Open Data via quatre fichiers couvrant les réseaux ferrés et de surface."
)

st.write(
    "Ces chiffres offrent une vision incomplète du trafic car ils excluent les tickets magnétiques (ticket T+, Forfait Mobilis, Forfait Paris Visite, etc) et les fraudeurs."
)

# Chargement des données.

filepath = os.path.join("..", "data", "processed", "validations_fusion.csv")
df = pd.read_csv(filepath)

# Validations par station.

st.header("Validations par station.")

st.write("Top 5 validations par station.")

# Sélectionner nom station et nombre de validations.
stations_validations_df = df[["nom_zdc", "nb_vald"]].copy()

# Grouper par station et somme des validations.
top_stations_df = (
    stations_validations_df.groupby("nom_zdc")["nb_vald"].sum().reset_index()
)

# Tri pour avoir le top.
top_stations_df = top_stations_df.sort_values(by="nb_vald", ascending=False)

fig = px.bar(top_stations_df.head(), x="nom_zdc", y="nb_vald")
fig.update_traces(marker_color="#64B5F6")

fig.update_xaxes(title_text=None)
fig.update_yaxes(title_text="Validations")

fig

# Stations où il y a le moins de validations.

st.write("Station où il y a le moins de validations.")

fig = px.bar(top_stations_df.tail(), x="nom_zdc", y="nb_vald")
fig.update_traces(marker_color="#ABD8FD")

fig.update_xaxes(title_text=None)
fig.update_yaxes(title_text="Validations")

fig

# Maps : carte des stations avec validations.

st.write("Carte des Stations.")

degrade_couleur = ["#4EA8DE", "#0077B6", "#03045E"]

fig = px.scatter_mapbox(
    df[["nom_zdc", "nb_vald", "latitude", "longitude"]]
    .groupby(["nom_zdc", "latitude", "longitude"])["nb_vald"]
    .sum()
    .reset_index(),
    lat="latitude",
    lon="longitude",
    hover_name="nom_zdc",
    size="nb_vald",
    color="nb_vald",
    color_continuous_scale=degrade_couleur,
    mapbox_style="carto-positron",
    width=1300,
    height=600,
)

fig


# Validations par catégorie de titre.

st.header("Validations par catégorie de titre.")

# Sélectionner catégorie de titre et nombre de validations.
categorie_titre_validations_df = df[["categorie_titre", "nb_vald"]].copy()

# Grouper par catégorie de titre et somme des validations.
top_categorie_titre_df = (
    categorie_titre_validations_df.groupby("categorie_titre")["nb_vald"]
    .sum()
    .reset_index()
)

# Tri pour avoir le top.
top_categorie_titre_df = top_categorie_titre_df.sort_values(
    by="nb_vald", ascending=True
)  # Tri inversé pour l'affichage graphique.

fig = px.bar(top_categorie_titre_df, x="nb_vald", y="categorie_titre")
fig.update_traces(marker_color="#64B5F6")

fig.update_xaxes(title_text="Validations")
fig.update_yaxes(title_text=None)

fig


# Validations par ligne de transport.

st.header("Validations par ligne de transport.")

st.write("Validations par ligne.")

# Lire csv de validations par ligne.
lignes_filepath = os.path.join("..", "data", "processed", "validations_ligne.csv")
lignes_df = pd.read_csv(lignes_filepath)

fig = px.bar(
    lignes_df,
    x="Ligne",
    y="somme_nb_vald",
)
fig.update_traces(marker_color="#64B5F6")

fig.update_xaxes(title_text=None)
fig.update_yaxes(title_text="Validations")

fig

st.write("Top 5 lignes.")

# Top lignes.
top_lignes_df = lignes_df.sort_values(by="somme_nb_vald", ascending=False).head()

fig = px.bar(top_lignes_df, x="Ligne", y="somme_nb_vald")
fig.update_traces(marker_color="#64B5F6")

fig.update_xaxes(title_text=None)
fig.update_yaxes(title_text="Validations")

fig


# Corrélation entre validations et nombre de lignes de transport par station.

st.header("Corrélation entre validations et nombre de lignes de transport par station.")

# Regroupement par station.
validations_lignes_df = (
    df.groupby("nom_zdc").agg({"nb_lignes": "max", "nb_vald": "sum"}).reset_index()
)

# Tri par nombre de lignes de transport disponible par station.
validations_lignes_df.sort_values(by="nb_lignes", ascending=False)

fig = px.scatter(
    validations_lignes_df,
    x="nb_lignes",
    y="nb_vald",
    hover_data=["nom_zdc"],
    size="nb_vald",
)
fig.update_traces(marker_color="#64B5F6")

fig.update_xaxes(title_text="Nombre de lignes par station")
fig.update_yaxes(title_text="Validations")

fig
