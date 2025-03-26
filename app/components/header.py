# header.py
import streamlit as st
from streamlit_navigation_bar import st_navbar


# Esconde o menu padrão do Streamlit e a sidebar
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

def render_navbar():
    # CSS da animação (opcional) para fazer a navbar "descer" ao carregar
    st.markdown(
        """
        <style>
        @keyframes slideDown {
            0% {
                transform: translateY(-100%);
            }
            100% {
                transform: translateY(0);
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Dicionário de estilos para customizar a aparência do st_navbar
    styles = {
        "nav": {
            "background-color": "#000000",             # Fundo preto
            "box-shadow": "0 2px 5px rgba(0,0,0,0.5)",
            "padding": "0.5rem 1rem",
            "animation": "slideDown 0.5s ease-in-out", # Animação "slideDown"
            "position": "sticky",                      # Mantém a barra no topo ao rolar
            "top": "0",
            "z-index": "999",
        },
        "div": {
            "display": "flex",
            "justify-content": "space-around",
            "align-items": "center",
            "max-width": "100%",
            "margin": "0 auto",
        },
        "span": {
            "color": "#FFFFFF",                        # Texto branco
            "margin": "0 1rem",
            "padding": "0.5rem 1rem",
            "text-decoration": "none",
            "transition": "background-color 0.3s ease",
            "border-radius": "4px",
            "font-weight": "500",                      # Deixa o texto mais "forte"
        },
        "active": {
            "background-color": "#FF0000",             # Destaque vermelho ao clicar
        },
        "hover": {
            "background-color": "#333333",             # Cinza escuro ao passar o mouse
        },
    }

    # Lista de páginas que serão exibidas na navbar
    pages = ["Home", "Preenchimento", "Sobre", "Contato"]

    # Cria e retorna a navbar, armazenando qual página foi selecionada
    selected_page = st_navbar(pages, styles=styles, key="navbar_main")
    return selected_page


# Exemplo de teste local
if __name__ == "__main__":
    st.set_page_config(page_title="Exemplo de Navbar", layout="wide")
    selecionado = render_navbar()
    st.write(f"Você selecionou: {selecionado}")
