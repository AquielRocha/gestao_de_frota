import streamlit as st
import pandas as pd
from app.services.auth import check_user_logged_in
from app.services.frota_2025_service import get_veiculos_by_setor_ano

def run():
    # Verifica se o usuário está logado
    check_user_logged_in()
    
    # O setor armazenado no login do usuário é usado para filtrar os veículos
    setor = st.session_state.user["setor_id"]
    st.title(f"Equipamentos 2025")
    
    # Busca os veículos da tabela 'frota' para o setor logado
    rows, columns = get_veiculos_by_setor_ano(setor)
    
    if rows:
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)
    else:
        st.info("Nenhum veículo encontrado para este setor.")
