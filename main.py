import streamlit as st
from streamlit_option_menu import option_menu

# Configurer la page principale
st.set_page_config(
    page_title="Navigation entre Pages",
    layout="wide",
    page_icon="🌐"
)

# Fonction pour gérer les pages
def navigate():
    if "page" not in st.session_state:
        st.session_state.page = "Analyse et Courbes"  # Page par défaut

    # Barre latérale de navigation
    with st.sidebar:
        choix = option_menu(
            "Menu de Navigation",
            ["Analyse et Courbes", "KPI et Cartes"],
            icons=["bar-chart", "map"],
            menu_icon="menu-app",
            default_index=0 if st.session_state.page == "Analyse et Courbes" else 1,
            styles={
                "container": {"padding": "5px", "background-color": "#f0f2f6"},
                "icon": {"color": "blue", "font-size": "25px"},
                "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "blue"},
            },
        )
        # Mettre à jour la page sélectionnée
        st.session_state.page = choix

    # Charger la page sélectionnée
    if st.session_state.page == "Analyse et Courbes":
        import page1
    elif st.session_state.page == "KPI et Cartes":
        import page2

# Appeler la fonction de navigation
navigate()
