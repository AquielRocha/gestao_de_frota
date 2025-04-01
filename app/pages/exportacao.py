import streamlit as st
from app.services.auth import check_user_logged_in

def run():
    check_user_logged_in()

    st.title("exportação do sistema Sistema")
    st.write("exportação de Gestão de Frota...")
