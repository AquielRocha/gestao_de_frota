import streamlit as st
from app.services.auth import check_user_logged_in

def run():
    check_user_logged_in()

    st.title("Página de Preenchimento")
    st.write("Formulário ou funcionalidades de preenchimento...")
