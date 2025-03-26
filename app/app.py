# main.py
import streamlit as st
import components.header as header
from pages.home import main as home_main

# Configuração da página
st.set_page_config(page_title="Gestão de Frota", layout="wide")

# Esconde o menu padrão do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# Renderiza o cabeçalho customizado
header.render_header()

# Captura os parâmetros da URL sem chamar a função
query_params = st.query_params
page = query_params.get("page", ["home"])[0]


if page == "home":
    home_main()
elif page == "about":
    st.title("Sobre Nós")
elif page == "contact":
    st.title("Contato")
else:
    st.error("Página não encontrada!")
