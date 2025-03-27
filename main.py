import streamlit as st
from app.services import app as frota_app

st.set_page_config(page_title="Gestão de Frota 2025", layout="wide")

# Executar app principal
def main():
    frota_app.run()

if __name__ == "__main__":
    main()