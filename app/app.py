import streamlit as st

# Este comando precisa ser o primeiro a gerar saída
st.set_page_config(page_title="Gestão de Frota", layout="wide")

# Após configurar a página, importe os outros módulos
import components.header as header
from pages.home import main as home_main

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
