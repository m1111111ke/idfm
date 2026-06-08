import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.title("Ile-de-France Mobilités : Analyse de données de validation de titres de transport")
st.write("Sources : Plateforme Régionale d'Information pour la Mobilité (PRIM) d'Ile-de-France Mobilités.")

filepath = os.path.join("..","data","processed","validations_fusion.csv")
df = pd.read_csv(filepath)

lignes = ['RER A', 'RER B', 'RER C', 'RER D', 'RER E', 'METRO 1', 'METRO 2', 'METRO 3', 'METRO 3bis','METRO 4', 'METRO 5', 'METRO 6', 'METRO 7', 'METRO 7bis','METRO 8', 'METRO 9', 'METRO 10', 'METRO 11', 'METRO 12', 'METRO 13', 'METRO 14', 'TRAIN H', 'TRAIN J', 'TRAIN K', 'TRAIN L', 'TRAIN N', 'TRAIN P', 'TRAIN R', 'TRAIN V', 'TRAM 1', 'TRAM 2', 'TRAM 3', 'TRAM 3a', 'TRAM 3b', 'TRAM 4', 'TRAM 5', 'TRAM 6', 'TRAM 7', 'TRAM 8', 'TRAM 9', 'TRAM 10', 'TRAM 11', 'TRAM 12', 'TRAM 13', 'TRAM 14', 'CABLE 1', 'CDGVAL', 'FUNICULAIRE MONTMARTRE']

lignes_df = pd.DataFrame({
    "Ligne": lignes,
    "somme_nb_vald": [df[df["res_com"].str.contains(l, na=False)]["nb_vald"].sum() for l in lignes]
})

fig = px.histogram(lignes_df, x="Ligne", y="somme_nb_vald",)
fig.update_traces(marker_color='#64B5F6')
fig

