import streamlit as st
from app.pages import home, preenchimento, sobre

# Inicializa usuário na sessão
if "usuario" not in st.session_state:
    st.session_state.usuario = None

def run():
    st.sidebar.title("Menu")
    opcoes = ["Início", "Preenchimento", "Sobre"]
    escolha = st.sidebar.radio("Ir para", opcoes)

    if escolha == "Início":
        home.show()
    elif escolha == "Preenchimento":
        preenchimento.show()
    elif escolha == "Sobre":
        sobre.show()
