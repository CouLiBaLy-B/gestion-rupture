import streamlit as st
import requests

# Configuration
st.set_page_config(
    page_title="Recherche",
    page_icon="images/logo.png",
    layout="wide",
    initial_sidebar_state="auto",
)
change_footer_style = """
            <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
            </style>
            """
st.markdown(change_footer_style, unsafe_allow_html=True)


def get_product_info(EAN):
    url = f"https://world.openfoodfacts.org/api/v0/product/{EAN}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Product not found"}


st.title("""Bienvenue sur notre site de web scraping dédié à la recherche d’informations sur les produits disponibles sur Open Food Facts! 🎉""")

# Test de la fonction
EAN = st.text_input("EAN", "0737628064502")  # remplacer par l'EAN du produit
if EAN:
    product_info = get_product_info(EAN)
    st.json(product_info)
