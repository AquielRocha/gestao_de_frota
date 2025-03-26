import os
import streamlit as st
from streamlit_navigation_bar import st_navbar

# Importa as funções principais de cada página
from pages.home import main as home_main
from pages.preenchimento import main as preenchimento_main
from pages.sobre import main as sobre_main

# Configuração da página
st.set_page_config(page_title="Home", layout="wide", initial_sidebar_state="collapsed")

# Esconde a sidebar e menu padrão do Streamlit
hide_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# Importa fonte moderna do Google Fonts
custom_fonts = """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
"""
st.markdown(custom_fonts, unsafe_allow_html=True)

# Lista de páginas que aparecerão na navbar
pages = ["Home", "Preenchimento", "Sobre", "Contato"]

# Caso queira associar algum link externo a um item, adicione aqui
urls = {
    # "Contato": "https://seulink.com/contato"  # Exemplo
}

# Estilos customizados para a navbar
styles = {
    "nav": {
        "background-color": "#1E293B",  # Azul escuro (tailwind slate-800)
        "justify-content": "left",
        "padding": "10px 20px",
    },
    "img": {
        "padding-right": "10px",
    },
    "span": {
        "color": "white",
        "padding": "18px 28px",
        "font-weight": "600",
        "border-radius": "6px",
        "transition": "background-color 0.3s ease",
    },
    "active": {
        "font-weight": "600",
        "padding": "12px 18px",
        "border-radius": "6px",
    }
}

# Opções da navbar
options = {
    "show_menu": False,
    "show_sidebar": False,
}

# Renderiza a navbar e obtém a página selecionada
page = st_navbar(
    pages,
    urls=urls,
    styles=styles,
    options=options,
)

# Mapeamento das páginas para suas respectivas funções
functions = {
    "Home": home_main,
    "Preenchimento": preenchimento_main,
    "Sobre": sobre_main,
    "Contato": lambda: st.write("Página de contato"),
}

# Chama a função correspondente à página selecionada
go_to = functions.get(page)
if go_to:
    go_to()
else:
    st.error("Página não encontrada!")
