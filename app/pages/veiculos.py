import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from app.services.auth import check_user_logged_in
from app.services.frota_2025_service import get_veiculos_by_setor_ano

def run():
    check_user_logged_in()
    setor = st.session_state.user["setor_id"]
    st.title("📋 Equipamentos 2025")

    rows, columns = get_veiculos_by_setor_ano(setor)

    if not rows:
        st.info("Nenhum veículo encontrado para este setor.")
        return

    df = pd.DataFrame(rows, columns=columns)
    df = df.drop(columns=['id', 'usuario_id', 'setor_id'], errors='ignore')

    # Remove vírgulas de textos
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.replace(',', '', regex=False)

    # Converte inteiros corretamente
    for col in df.select_dtypes(include=['int']).columns:
        df[col] = df[col].astype(int)

    # Renomeia colunas com ortografia correta
    colunas_legiveis = {
        "data_preenchimento": "Data de Preenchimento",
        "tipo_bem": "Tipo do Bem",
        "subtipo_bem": "Subtipo",
        "placa": "Placa",
        "numero_chassi": "Número do Chassi",
        "renavam": "RENAVAM",
        "numero_patrimonio": "Nº Patrimônio",
        "proprietario": "Proprietário",
        "marca": "Marca",
        "modelo": "Modelo",
        "ano_fabricacao": "Ano de Fabricação",
        "ano_modelo": "Ano do Modelo",
        "cor": "Cor",
        "combustivel": "Combustível",
        "status": "Status",
        "observacao": "Observação",
        "adicionar_mais": "Adição Extra?"
    }
    df = df.rename(columns=colunas_legiveis)

    # 🎯 Campos de filtro
    with st.expander("🔎 Filtrar Equipamentos"):
        col1, col2, col3 = st.columns(3)
        tipo = col1.selectbox("Tipo do Bem", options=["Todos"] + sorted(df["Tipo do Bem"].dropna().unique().tolist()))
        marca = col2.selectbox("Marca", options=["Todos"] + sorted(df["Marca"].dropna().unique().tolist()))
        modelo = col3.selectbox("Modelo", options=["Todos"] + sorted(df["Modelo"].dropna().unique().tolist()))
        
        col4, col5, col6 = st.columns(3)
        placa = col4.text_input("Buscar por Placa")
        status = col5.selectbox("Status", options=["Todos"] + sorted(df["Status"].dropna().unique().tolist()))
        ano = col6.selectbox("Ano de Fabricação", options=["Todos"] + sorted(df["Ano de Fabricação"].dropna().unique().tolist()))

        # Aplica os filtros
        if tipo != "Todos":
            df = df[df["Tipo do Bem"] == tipo]
        if marca != "Todos":
            df = df[df["Marca"] == marca]
        if modelo != "Todos":
            df = df[df["Modelo"] == modelo]
        if status != "Todos":
            df = df[df["Status"] == status]
        if ano != "Todos":
            df = df[df["Ano de Fabricação"] == ano]
        if placa:
            df = df[df["Placa"].str.contains(placa, case=False, na=False)]

    # Tabela interativa
    st.subheader("📑 Equipamentos Encontrados")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(editable=False, groupable=True)
    grid_options = gb.build()

    AgGrid(df, gridOptions=grid_options, theme="streamlit", height=500)

