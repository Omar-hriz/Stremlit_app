import pandas as pd
import streamlit as st
import plotly.express as px

# Charger les données nettoyées
file_path = "data_cleaned_sample.csv"
data = pd.read_csv(file_path)

# Charger les résultats des comparaisons des prix (Étape 7)
produit_fichiers = {
    "Gazole": "sampled_comparaison_Gazole.csv",
    "SP95": "sampled_comparaison_SP95.csv",
    "SP98": "sampled_comparaison_SP98.csv",
    "E10": "sampled_comparaison_E10.csv",
    "E85": "sampled_comparaison_E85.csv",
    "GPLc": "sampled_comparaison_GPLc.csv"
}

# Nettoyer la sidebar
st.sidebar.empty()

st.title("📊 Analyse des Stations d'Essence et Comparaisons de Prix")
st.markdown("Bienvenue dans cette application d'analyse interactive des stations d'essence.")

# Section 1 : Analyse des enseignes
st.header("⚡ Analyse des Enseignes")
st.subheader("Filtrer les enseignes ayant plus de 100 stations")

stations_par_enseigne = (
    data.groupby("Enseigne")["id"]
    .nunique()
    .reset_index()
    .rename(columns={"id": "Nombre de stations"})
)

enseignes_100plus = stations_par_enseigne[stations_par_enseigne["Nombre de stations"] > 100].sort_values(
    by="Nombre de stations", ascending=False
)

col1, col2 = st.columns([2, 3])

with col1:
    st.write(f"Nombre total d'enseignes ayant plus de 100 stations : **{enseignes_100plus.shape[0]}**")
    st.dataframe(enseignes_100plus)

with col2:
    fig_enseignes = px.bar(
        enseignes_100plus,
        x="Enseigne",
        y="Nombre de stations",
        title="Nombre de Stations par Enseigne",
        text="Nombre de stations"
    )
    st.plotly_chart(fig_enseignes, use_container_width=True)

# Comparaisons des prix
st.header("💰 Comparaisons des Prix par Produit")
produit_selectionne = st.selectbox("Choisissez un produit à analyser :", list(produit_fichiers.keys()))
comparaison_data = pd.read_csv(produit_fichiers[produit_selectionne])

dates_disponibles = comparaison_data["Date"].unique()
date_selectionnee = st.selectbox("Choisissez une date :", dates_disponibles)

comparaison_par_date = comparaison_data[comparaison_data["Date"] == date_selectionnee]

st.subheader(f"Comparaison des Positions par Enseigne pour {produit_selectionne}")
fig_enseignes_positions = px.bar(
    comparaison_par_date.melt(id_vars=["Enseigne Concurrente"], value_vars=["Inférieur", "Supérieur", "Égal"]),
    x="Enseigne Concurrente",
    y="value",
    color="variable",
    barmode="stack"
)
st.plotly_chart(fig_enseignes_positions, use_container_width=True)
