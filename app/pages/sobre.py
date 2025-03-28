import streamlit as st
from app.services.auth import check_user_logged_in

def run():
    check_user_logged_in()

    st.title("Sobre o Sistema")
    st.write("Informações sobre o sistema de Gestão de Frota...")
