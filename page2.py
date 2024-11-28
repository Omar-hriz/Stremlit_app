import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import json

# Charger les données nettoyées et fichiers JSON
file_path = "data_cleaned.csv"
data = pd.read_csv(file_path)
with open("concurrents.json", "r") as f:
    concurrents_dict = json.load(f)

st.title("💡 KPI et Cartes Interactives")

list_product = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]

# Étape A : Calcul des KPIs
st.header("📊 Indicateurs Clés de Performance (KPI)")
# Produit sélectionné pour les KPIs
produit_selectionne = st.selectbox("Choisissez un produit pour les KPIs :", list_product)

# Créer une liste des colonnes à exclure sans modifier la liste originale
colonnes_a_garder = [produit_selectionne, "Enseigne"]

# Filtrer les colonnes nécessaires et calculer les KPIs
kpi_data = (
    data[colonnes_a_garder]
    .groupby("Enseigne")
    .mean()
    .reset_index()
)

# Filtrer les enseignes d'intérêt
kpi_data = kpi_data[
    kpi_data["Enseigne"].isin(["Carrefour", "Auchan", "E.Leclerc", "Total Access", "Intermarché", "Système U"])
]

st.dataframe(kpi_data)

# Étape B : Carte Interactive
st.header("🗺️ Carte Interactive des Stations")
station_selectionnee = st.selectbox("Choisissez une station Carrefour :", list(concurrents_dict.keys()))
carrefour_coords = data[data["id"] == int(station_selectionnee)][["Latitude", "Longitude"]].values[0]

m = folium.Map(location=[carrefour_coords[0] / 1000000, carrefour_coords[1] / 1000000], zoom_start=10)
folium.Marker(location=[carrefour_coords[0] / 1000000, carrefour_coords[1] / 1000000],
              popup="Carrefour", icon=folium.Icon(color="blue")).add_to(m)

for concurrent in concurrents_dict[station_selectionnee]:
    concurrent_coords = data[data["id"] == int(concurrent)][["Latitude", "Longitude"]].values[0]
    folium.Marker(location=[concurrent_coords[0] / 1000000, concurrent_coords[1] / 1000000],
                  popup="Concurrent", icon=folium.Icon(color="green")).add_to(m)

st_folium(m, width=800, height=500)

# Étape C : Tableau de Comparaison des Prix
st.header("📋 Tableau de Comparaison des Prix")
tableau_data = data[data["id"].isin([int(station_selectionnee)] + concurrents_dict[station_selectionnee])]
tableau_data = tableau_data[tableau_data["Produit"] == produit_selectionne].sort_values("Prix", ascending=False)
st.dataframe(tableau_data.style.apply(
    lambda x: ["background: lightgreen" if x.name == int(station_selectionnee) else "" for _ in x], axis=1))
