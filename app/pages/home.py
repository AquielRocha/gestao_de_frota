import streamlit as st
from app.services.auth import check_user_logged_in

def run():
    check_user_logged_in()
    st.title("Página Home")
    st.write(f"Bem-vindo, {st.session_state.user['nome']}!")
    st.write("Conteúdo exclusivo para usuários logados.")
