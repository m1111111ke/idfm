import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px

st.title("Ile-de-France Mobilités : Analyse de données de validation de titres de transport.")
st.write("Sources : Plateforme Régionale d'Information pour la Mobilité (PRIM) d'Ile-de-France Mobilités.")


# Validations par station.

st.header("Top 5 Validations par station.")

filepath = os.path.join("..","data","processed","validations_fusion.csv")
df = pd.read_csv(filepath)

# Sélectionner nom station et nombre de validations.
stations_validations_df = df[["nom_zdc","nb_vald"]].copy()

# Grouper par station et somme des validations.
top_stations_df = stations_validations_df.groupby("nom_zdc")["nb_vald"].sum().reset_index()

# Tri pour avoir le top.
top_stations_df = top_stations_df.sort_values(by="nb_vald", ascending=False)

fig = px.histogram(top_stations_df.head(), x="nom_zdc", y="nb_vald",)
fig.update_traces(marker_color='#64B5F6')
fig

# Stations où il y a le moins de validations.

st.write("Station où il y a le moins de validations.")

fig = px.histogram(top_stations_df.tail(), x="nom_zdc", y="nb_vald",)
fig.update_traces(marker_color="#ABD8FD")
fig


# Validations par catégorie de titre.

st.header("Validations par catégorie de titre.")

# Sélectionner catégorie de titre et nombre de validations.
categorie_titre_validations_df = df[["categorie_titre","nb_vald"]].copy()

# Grouper par catégorie de titre et somme des validations.
top_categorie_titre_df = categorie_titre_validations_df.groupby("categorie_titre")["nb_vald"].sum().reset_index()

# Tri pour avoir le top.
top_categorie_titre_df = top_categorie_titre_df.sort_values(by="nb_vald", ascending=False)

fig = px.histogram(top_categorie_titre_df, x="categorie_titre", y="nb_vald",)
fig.update_traces(marker_color='#64B5F6')
fig


# Validations par ligne de transport.

st.header("Validations par ligne de transport.")

st.write("Validations par ligne.")

# Lire csv de validations par ligne.
lignes_filepath = os.path.join("..","data","processed","validations_ligne.csv")
lignes_df = pd.read_csv(lignes_filepath)

fig = px.histogram(lignes_df, x="Ligne", y="somme_nb_vald",)
fig.update_traces(marker_color='#64B5F6')
fig

st.write("Top 5 lignes.")

# Top lignes.
top_lignes_df = lignes_df.sort_values(by="somme_nb_vald", ascending=False).head()

fig = px.histogram(top_lignes_df, x="Ligne", y="somme_nb_vald",)
fig.update_traces(marker_color='#64B5F6')
fig


# Corrélation entre validations et nombre de lignes de transport par station.

st.header("Corrélation entre validations et nombre de lignes de transport par station.")

# Regroupement par station.
validations_lignes_df = (
    df.groupby("nom_zdc")
    .agg(
        {
            "nb_lignes": "max",
            "nb_vald": "sum"
        }
    )
    .reset_index()
)

# Tri par nombre de lignes de transport disponible par station.
validations_lignes_df.sort_values(by="nb_lignes", ascending=False)

fig = px.scatter(validations_lignes_df, x="nb_vald", y="nb_lignes", hover_data=['nom_zdc'], size="nb_vald")
fig.update_traces(marker_color='#64B5F6')
fig