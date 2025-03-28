import streamlit as st
import sqlite3
import pandas as pd
from app.services.auth import check_user_logged_in

def run():
    check_user_logged_in()
    st.title("ATUALIZAÇÃO DE INFORMAÇÕES - Gestão de Frota 2024")

    # 1. Conectar ao banco e carregar dados da tabela 'dimensao_frota_2024'
    conn = sqlite3.connect("app/database/veiculos.db")
    cursor = conn.cursor()

    # Carrega todos os dados de 'dimensao_frota_2024'
    df_dim = pd.read_sql_query("SELECT * FROM dimensao_frota_2024", conn)

    # Exemplo de colunas que podem existir em dimensao_frota_2024 (ajuste conforme sua tabela):
    #   - tipo_bem
    #   - subtipo_bem
    #   - proprietario
    #   - fabricante
    #   - modelo
    #   - tipo_combustivel
    #   - status
    #   - controle_desempenho
    #   etc.
    #
    # Usamos 'dropna().unique().tolist()' para criar listas de opções de cada coluna:
    tipos_bem = df_dim["tipo_bem"].dropna().unique().tolist() if "tipo_bem" in df_dim.columns else []
    subtipos_bem = df_dim["subtipo_bem"].dropna().unique().tolist() if "subtipo_bem" in df_dim.columns else []
    proprietarios = df_dim["proprietario"].dropna().unique().tolist() if "proprietario" in df_dim.columns else []
    fabricantes = df_dim["fabricante"].dropna().unique().tolist() if "fabricante" in df_dim.columns else []
    modelos = df_dim["modelo"].dropna().unique().tolist() if "modelo" in df_dim.columns else []
    combustiveis = df_dim["tipo_combustivel"].dropna().unique().tolist() if "tipo_combustivel" in df_dim.columns else []
    status_list = df_dim["status"].dropna().unique().tolist() if "status" in df_dim.columns else []
    controle_list = df_dim["controle_desempenho"].dropna().unique().tolist() if "controle_desempenho" in df_dim.columns else []

    # 2. Exibir o formulário com campos de input
    with st.form("form_frota_2024"):
        st.subheader("Informações dos veículos, equipamentos e embarcações")

        # Exemplos de campos do formulário (adapte ao que sua tela exibe):
        tipo_bem = st.selectbox("Tipo do Bem", tipos_bem)
        subtipo_bem = st.selectbox("Subtipo do Bem", subtipos_bem)
        prop = st.selectbox("Proprietário", proprietarios)
        placa = st.text_input("Placa")
        renavam = st.text_input("Renavam")
        chassi = st.text_input("Chassi")
        marca = st.selectbox("Marca/Fabricante", fabricantes)
        modelo = st.selectbox("Modelo", modelos)
        ano_fab = st.text_input("Ano Fabricação")
        ano_mod = st.text_input("Ano Modelo")
        tipo_comb = st.selectbox("Tipo de Combustível", combustiveis)
        stat = st.selectbox("Status", status_list)
        controle = st.selectbox("Controle de Desempenho", controle_list)
        uso_km = st.text_input("Uso (km ou horas)")
        cor = st.text_input("Cor")
        observacoes = st.text_area("Observações")

        # Botão de submissão do formulário
        submitted = st.form_submit_button("Salvar")

    # 3. Se o usuário clicar em "Salvar", inserir dados na tabela 'frota_2025'
    if submitted:
        try:
            insert_query = """
            INSERT INTO frota_2025 (
                tipo_bem,
                subtipo_bem,
                proprietario,
                placa,
                renavam,
                chassi,
                fabricante,
                modelo,
                ano_fabricacao,
                ano_modelo,
                tipo_combustivel,
                status,
                controle_desempenho,
                uso_km,
                cor,
                observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                tipo_bem,
                subtipo_bem,
                prop,
                placa,
                renavam,
                chassi,
                marca,
                modelo,
                ano_fab,
                ano_mod,
                tipo_comb,
                stat,
                controle,
                uso_km,
                cor,
                observacoes
            ))
            conn.commit()
            st.success("Dados inseridos com sucesso na tabela frota_2025!")
        except Exception as e:
            st.error(f"Erro ao inserir dados: {e}")

    conn.close()
