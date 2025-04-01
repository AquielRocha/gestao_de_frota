import streamlit as st
import pandas as pd
from app.services.auth import check_user_logged_in
from app.services.frota_2025_service import get_veiculos_by_setor_ano

def run():
    # 1) Verifica se o usuário está logado
    check_user_logged_in()
    
    # 2) O setor armazenado no login do usuário é usado para filtrar os veículos
    setor = st.session_state.user["setor_id"]
    st.title(f"Equipamentos 2025")
    
    # 3) Busca os veículos da tabela 'frota_2025' (ou outra) para o setor logado
    rows, columns = get_veiculos_by_setor_ano(setor)
    
    if rows:
        # 4) Converte o resultado em DataFrame e exibe
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)
    else:
        # 5) Se não tiver resultados, mostra uma mensagem
        st.info("Nenhum veículo encontrado para este setor.")
