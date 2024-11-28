import streamlit as st

# Titre principal
st.title("Application Principale")

# Message d'introduction
st.markdown("Bienvenue dans l'application principale. Utilisez la barre latérale pour naviguer.")

# Navigation
if st.sidebar.button("Aller à la Page 1"):
    st.switch_page("page1")

if st.sidebar.button("Aller à la Page 2"):
    st.switch_page("page2")
