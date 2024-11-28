import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import json

# Charger les données nettoyées et fichiers JSON
file_path = "data_cleaned.csv"
carrefour_file = "stations_carrefour.csv"
concurrents_file = "stations_autres.csv"

carrefour_data = pd.read_csv(carrefour_file)
concurrents_data = pd.read_csv(concurrents_file)

with open("concurrents.json", "r") as f:
    concurrents_dict = json.load(f)

# Configurer la page
st.set_page_config(
    page_title="Analyse des Stations",
    layout="wide",
    page_icon="⛽"
)

# Charger les produits et autres constantes
list_product = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
selected_brands_kpi = ["Carrefour", "Auchan", "E.Leclerc", "Total Access", "Intermarché", "Système U"]

# Sidebar pour les filtres
st.sidebar.header("Filtres")
produit_selectionne = st.sidebar.selectbox("Choisissez un produit :", list_product)

# Sélecteur de date unique
carrefour_data["Date"] = pd.to_datetime(carrefour_data["Date"], errors="coerce")
concurrents_data["Date"] = pd.to_datetime(concurrents_data["Date"], errors="coerce")

dates_disponibles = carrefour_data["Date"].dropna().sort_values().unique()
date_selectionnee = st.sidebar.date_input(
    "Choisissez une date :",
    value=dates_disponibles.min(),
    min_value=dates_disponibles.min(),
    max_value=dates_disponibles.max(),
    key="date_selection_unique"
)

# Sélecteur de station Carrefour
station_selectionnee = st.sidebar.selectbox(
    "Choisissez une station Carrefour :", list(concurrents_dict.keys())
)

# Filtrage des concurrents visibles
concurrents_ids = concurrents_dict[station_selectionnee]
concurrents_visible_data = concurrents_data[concurrents_data["id"].isin(map(int, concurrents_ids))]

# Sélecteur de marques pour les courbes
marques_disponibles = concurrents_visible_data["Enseigne"].unique()
marques_selectionnees = st.sidebar.multiselect(
    "Filtrez les concurrents par enseigne (pour les courbes) :",
    options=marques_disponibles,
    default=marques_disponibles
)

# Section principale
st.title("⛽ Analyse des Stations d'Essence")
st.markdown("""
    Explorez les données des stations Carrefour et de leurs concurrents pour une date spécifique, visualisez les prix des carburants, et analysez les indicateurs clés.
""")

# Étape A : KPI
st.header("📊 Indicateurs Clés de Performance (KPI)")

# Filtrer les données pour la date sélectionnée
carrefour_filtered = carrefour_data[carrefour_data["Date"] == pd.to_datetime(date_selectionnee)]
concurrents_filtered = concurrents_visible_data[concurrents_visible_data["Date"] == pd.to_datetime(date_selectionnee)]

# Calculer les KPI pour les enseignes sélectionnées
kpi_data = (
    concurrents_filtered[[produit_selectionne, "Enseigne"]]
    .groupby("Enseigne")
    .mean(numeric_only=True)
    .reset_index()
)

# Limiter les KPI aux marques spécifiques
kpi_data = kpi_data[kpi_data["Enseigne"].isin(selected_brands_kpi)]

# Afficher les KPI sous forme de cartes
col1, col2, col3 = st.columns(3)
for idx, row in kpi_data.iterrows():
    enseigne, prix_moyen = row["Enseigne"], row[produit_selectionne]
    if idx % 3 == 0:
        col = col1
    elif idx % 3 == 1:
        col = col2
    else:
        col = col3
    col.metric(label=f"Prix moyen - {enseigne}", value=f"{prix_moyen:.2f} €")

# Étape B : Carte Interactive et Tableau
st.header("🗺️ Carte Interactive et Tableau des Concurrents")

carrefour_coords = carrefour_filtered[carrefour_filtered["id"] == int(station_selectionnee)][["Latitude", "Longitude"]].values[0]
if not (-90 <= carrefour_coords[0] <= 90 and -180 <= carrefour_coords[1] <= 180):
    carrefour_coords = [carrefour_coords[0] / 100000, carrefour_coords[1] / 100000]

m = folium.Map(location=[carrefour_coords[0], carrefour_coords[1]], zoom_start=12)
folium.Marker(
    location=[carrefour_coords[0], carrefour_coords[1]],
    popup="Carrefour",
    icon=folium.Icon(color="blue")
).add_to(m)

# Ajouter les concurrents visibles
for _, concurrent in concurrents_filtered.iterrows():
    concurrent_coords = concurrent[["Latitude", "Longitude"]].values
    if not (-90 <= concurrent_coords[0] <= 90 and -180 <= concurrent_coords[1] <= 180):
        concurrent_coords = [concurrent_coords[0] / 100000, concurrent_coords[1] / 100000]

    folium.Marker(
        location=[concurrent_coords[0], concurrent_coords[1]],
        popup=f"{concurrent['Enseigne']} - {concurrent[produit_selectionne]:.2f} €",
        icon=folium.Icon(color="green")
    ).add_to(m)

st_folium(m, width=1600, height=800)

# Tableau des concurrents
st.subheader("📋 Tableau des Concurrents sur la Carte")
tableau_data = concurrents_filtered[["Enseigne", produit_selectionne, "Adresse", "Ville"]].copy()
tableau_data.rename(columns={produit_selectionne: "Prix (€)"}, inplace=True)
st.dataframe(tableau_data.sort_values(by="Prix (€)"))

# Étape C : Courbes de Prix
st.header("📈 Évolution des Prix des Carburants")

# Préparer les données pour Carrefour
carrefour_prices = carrefour_filtered[carrefour_filtered["id"] == int(station_selectionnee)][["Date", produit_selectionne]].copy()
carrefour_prices["Type"] = "Carrefour"

# Préparer les données pour les concurrents
concurrents_prices = concurrents_filtered[concurrents_filtered["Enseigne"].isin(marques_selectionnees)][
    ["Date", produit_selectionne, "Enseigne"]
].copy()
concurrents_prices["Type"] = concurrents_prices["Enseigne"]

# Renommer les colonnes pour uniformiser
carrefour_prices.rename(columns={produit_selectionne: "Prix"}, inplace=True)
concurrents_prices.rename(columns={produit_selectionne: "Prix"}, inplace=True)

# Combiner les données pour l'affichage
prices_data = pd.concat([carrefour_prices, concurrents_prices], ignore_index=True)

# Regrouper par jour et type pour simplifier la courbe
prices_data_grouped = prices_data.groupby(["Date", "Type"], as_index=False).mean(numeric_only=True)

# Convertir les dates en format compatible avec Streamlit
prices_data_grouped["Date"] = pd.to_datetime(prices_data_grouped["Date"])
date_min = prices_data_grouped["Date"].min().date()  # Convertir en `date`
date_max = prices_data_grouped["Date"].max().date()  # Convertir en `date`

# Ajouter un sélecteur de plage de dates
date_range = st.slider(
    "Sélectionnez une plage de dates pour afficher les prix :",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
    format="YYYY-MM-DD"
)

# Filtrer les données selon la plage de dates sélectionnée
prices_data_filtered = prices_data_grouped[
    (prices_data_grouped["Date"] >= pd.Timestamp(date_range[0])) &
    (prices_data_grouped["Date"] <= pd.Timestamp(date_range[1]))
]

# Afficher la courbe des prix pour la plage de dates sélectionnée
fig_prix = px.line(
    prices_data_filtered,
    x="Date",
    y="Prix",
    color="Type",
    title=f"Évolution des prix pour {produit_selectionne} ({date_range[0]} - {date_range[1]})",
    labels={"Prix": "Prix (€)", "Date": "Date", "Type": "Type de station"},
    markers=True
)

# Personnalisation du graphique
fig_prix.update_layout(
    title=dict(x=0.5, font=dict(size=16)),
    xaxis_title="Date",
    yaxis_title="Prix (€)",
    legend_title="Type de station",
    template="plotly_white"
)

# Afficher le graphique
st.plotly_chart(fig_prix, use_container_width=True)

