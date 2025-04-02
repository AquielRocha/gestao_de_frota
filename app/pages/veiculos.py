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
        # 4) Converte o resultado em DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # 5) Remove as colunas 'id' e 'setor_id', se existirem
        df = df.drop(columns=['id', 'usuario_id', 'setor_id'], errors='ignore')
        
        # 6) Remove todas as vírgulas das colunas do tipo string
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.replace(',', '', regex=False)
        
        # 7) Tenta converter todas as colunas numéricas para inteiros
        for col in df.select_dtypes(include=['int']).columns:
            df[col] = df[col].astype(int)
        
        # 8) Exibe o DataFrame
        st.dataframe(df)
    else:
        # 9) Se não tiver resultados, mostra uma mensagem
        st.info("Nenhum veículo encontrado para este setor.")
