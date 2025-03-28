import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import re
from app.services.auth import check_user_logged_in

# Função para carregar os dados filtrados por centro_custo
def carregar_dados_frota(centro_custo):
    try:
        conn = sqlite3.connect("app/database/veiculos.db")
        # Verifica se a tabela "frota" existe
        tabela = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='frota'", conn
        )
        if tabela.empty:
            st.error("A tabela 'frota' não existe no banco de dados. Verifique se o nome da tabela está correto ou se ela foi criada.")
            return pd.DataFrame()  # Retorna um DataFrame vazio
        
        # Altera o filtro para usar a coluna 'centro_custo'
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
    centro_custo = usuario.get("setor_id")  # Pegando do campo correto

    if not centro_custo:
        st.error("Seu setor não foi definido. Verifique seu cadastro ou fale com o administrador.")
        return

    # Aplique a mesma substituição (regex) na variável antes de exibir no título
    centro_custo_display = re.sub(
        r"NOME NÃO ENCONTRADO ANTIGO NOME \((.+)\)", 
        r"\1", 
        centro_custo
    )

    st.title(f"Dados da Frota - Setor: {centro_custo_display}")
    st.write(f"Bem-vindo, **{usuario['nome']}**!")

    df = carregar_dados_frota(centro_custo)

    if df.empty:
        st.warning("Nenhum dado de frota encontrado para o seu setor.")
        return

    # Substitui valores que seguem o padrão na coluna do DataFrame
    df['centro_custo'] = df['centro_custo'].str.replace(
        r"NOME NÃO ENCONTRADO ANTIGO NOME \((.+)\)", 
        r"\1", 
        regex=True
    )

    # KPIs principais
    st.subheader("Resumo da Frota")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Equipamentos", len(df))
    col2.metric("Ativos", df[df["status"] == "Ativo"].shape[0])
    col3.metric("Tipos de Combustível", df["tipo_combustivel"].nunique())

    # Gráfico por modelo
    st.subheader("Distribuição por Modelo")
    grafico_modelos = df["modelo"].value_counts().reset_index()
    grafico_modelos.columns = ["Modelo", "Quantidade"]
    fig_modelo = px.bar(grafico_modelos, x="Modelo", y="Quantidade", title="Veículos/Equipamentos por Modelo")
    st.plotly_chart(fig_modelo)

    # Gráfico de uso
    st.subheader("Uso por Equipamento")
    df_uso = df.dropna(subset=["uso_km"])
    fig_uso = px.histogram(df_uso, x="uso_km", nbins=20, title="Distribuição do Uso (km/horas)")
    st.plotly_chart(fig_uso)

    # Tipo de controle
    st.subheader("Tipo de Controle de Uso")
    grafico_controle = df["controle_desempenho"].value_counts().reset_index()
    grafico_controle.columns = ["Tipo de Controle", "Quantidade"]
    fig_controle = px.pie(grafico_controle, names="Tipo de Controle", values="Quantidade", title="Tipos de Controle na Frota")
    st.plotly_chart(fig_controle)

    # Tabela detalhada
    st.subheader("Tabela Detalhada da Frota")
    st.dataframe(df[["identificacao", "modelo", "ano_fabricacao", "tipo_combustivel", "controle_desempenho", "uso_km", "status"]])
