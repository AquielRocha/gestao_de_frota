import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import re
from app.services.auth import check_user_logged_in

def carregar_dados_frota(centro_custo):
    try:
        conn = sqlite3.connect("app/database/veiculos.db")
        tabela = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='frota'", conn
        )
        if tabela.empty:
            st.error("A tabela 'frota' não existe no banco de dados.")
            return pd.DataFrame()
        query = "SELECT * FROM frota WHERE centro_custo = ?"
        df = pd.read_sql_query(query, conn, params=(centro_custo,))
    except Exception as e:
        st.error(f"Erro ao carregar os dados da frota: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def run():
    check_user_logged_in()
    usuario = st.session_state.user
    centro_custo = usuario.get("setor_id")

    if not centro_custo:
        st.error("Seu setor não foi definido. Verifique seu cadastro.")
        return

    centro_custo_display = re.sub(
        r"NOME NÃO ENCONTRADO ANTIGO NOME \((.+)\)", 
        r"\1", 
        centro_custo
    )

    st.title(f"📊 Dados da Frota - Setor: {centro_custo_display}")
    st.success(f"Bem-vindo, **{usuario['nome']}**!")

    df = carregar_dados_frota(centro_custo)

    if df.empty:
        st.warning("Nenhum dado de frota encontrado para o seu setor.")
        return

    df['centro_custo'] = df['centro_custo'].str.replace(
        r"NOME NÃO ENCONTRADO ANTIGO NOME \((.+)\)", 
        r"\1", 
        regex=True
    )

    # KPIs
    st.subheader("🔢 Resumo da Frota")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Equipamentos", len(df))
    col2.metric("Ativos", df[df["status"] == "Ativo"].shape[0])
    col3.metric("Tipos de Combustível", df["tipo_combustivel"].nunique())

    # Tabs para Gráficos e Tabela
    aba1, aba2 = st.tabs(["📈 Gráficos", "📋 Tabela Detalhada"])

    with aba1:
        st.subheader("Distribuição por Modelo")
        grafico_modelos = df["modelo"].value_counts().reset_index()
        grafico_modelos.columns = ["Modelo", "Quantidade"]
        fig_modelo = px.bar(grafico_modelos, x="Modelo", y="Quantidade", title="Veículos/Equipamentos por Modelo")
        st.plotly_chart(fig_modelo, use_container_width=True)

        st.subheader("Tipo de Controle de Uso")
        grafico_controle = df["controle_desempenho"].value_counts().reset_index()
        grafico_controle.columns = ["Tipo de Controle", "Quantidade"]
        fig_controle = px.pie(grafico_controle, names="Tipo de Controle", values="Quantidade", title="Tipos de Controle na Frota")
        st.plotly_chart(fig_controle, use_container_width=True)

    with aba2:
        st.subheader("🧾 Visualização Interativa da Tabela")
        with st.expander("🔍 Clique para visualizar os dados completos"):

            df_tabela = df[[ 
                "identificacao", "modelo", "ano_fabricacao", "tipo_combustivel",
                "controle_desempenho", "uso_km", "status"
            ]].rename(columns={
                "identificacao": "Identificação",
                "modelo": "Modelo",
                "ano_fabricacao": "Ano de Fabricação",
                "tipo_combustivel": "Tipo de Combustível",
                "controle_desempenho": "Controle de Desempenho",
                "uso_km": "Uso (km ou horas)",
                "status": "Status"
            })

            st.dataframe(
                df_tabela,
                use_container_width=True,
                hide_index=True,
                height=400,
                column_config={col: st.column_config.Column(label=col) for col in df_tabela.columns}
            )
