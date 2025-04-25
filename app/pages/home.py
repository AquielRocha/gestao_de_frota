import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.db import get_connection          # usa conexão centralizada
from app.services.auth import check_user_logged_in

# ------------------------------------------------------------------ #
# Consulta todos os equipamentos do setor do usuário                 #
# ------------------------------------------------------------------ #
def carregar_dados_frota(setor_codigo: int) -> pd.DataFrame:
    sql = """
        SELECT  e.*,
                s.nome  AS setor_nome,
                s.sigla AS setor_sigla
        FROM    equipamentos  e
        JOIN    setor         s ON s.codigo = e.centro_custo_uc
        WHERE   e.centro_custo_uc = ?
    """
    try:
        with get_connection() as con:
            df = pd.read_sql_query(sql, con, params=(setor_codigo,))
    except Exception as exc:
        st.error(f"Erro ao carregar a frota: {exc}")
        df = pd.DataFrame()

    return df


# ------------------------------------------------------------------ #
# Página                                                             #
# ------------------------------------------------------------------ #
def run():
    check_user_logged_in()
    usuario = st.session_state.user

    # ⚠️ campo vem da view get_user_info →  'setor_codigo'
    setor_codigo = usuario.get("setor_codigo")
    if not setor_codigo:
        st.error("Seu setor não está definido. Verifique seu cadastro.")
        return

    df = carregar_dados_frota(setor_codigo)
    if df.empty:
        st.warning("Nenhum equipamento encontrado para o seu setor.")
        return

    setor_nome = df.iloc[0]["setor_nome"]
    st.title(f"📊 Frota – Setor: {setor_nome}")
    st.success(f"Bem-vindo, **{usuario['nome']}**!")

    # ---------------- KPIs ---------------- #
    st.subheader("🔢 Resumo da Frota")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Equipamentos", len(df))
    col2.metric("Ativos", df[df["status"] == "Ativo"].shape[0])
    col3.metric("Tipos de Combustível", df["tipo_combustivel"].nunique())

    # ---------------- Abas ---------------- #
    aba_graf, aba_tab = st.tabs(["📈 Gráficos", "📋 Tabela"])

    with aba_graf:
        st.subheader("Distribuição por Modelo")
        modelos = df["modelo"].value_counts().reset_index()
        modelos.columns = ["Modelo", "Quantidade"]
        st.plotly_chart(
            px.bar(modelos, x="Modelo", y="Quantidade",
                   title="Equipamentos por Modelo"),
            use_container_width=True
        )

        st.subheader("Tipo de Controle de Uso")
        controle = df["controle_desempenho"].value_counts().reset_index()
        controle.columns = ["Tipo de Controle", "Quantidade"]
        st.plotly_chart(
            px.pie(controle, names="Tipo de Controle", values="Quantidade",
                   title="Tipos de Controle na Frota"),
            use_container_width=True
        )

    with aba_tab:
        st.subheader("🧾 Tabela Detalhada")
        mostra = df[[
            "identificacao", "modelo", "ano_fabricacao",
            "tipo_combustivel", "controle_desempenho",
            "uso_km", "status"
        ]].rename(columns={
            "identificacao":       "Identificação",
            "modelo":              "Modelo",
            "ano_fabricacao":      "Ano de Fabricação",
            "tipo_combustivel":    "Tipo de Combustível",
            "controle_desempenho": "Controle de Desempenho",
            "uso_km":              "Uso (km/horas)",
            "status":              "Status"
        })

        st.dataframe(
            mostra,
            use_container_width=True,
            hide_index=True,
            height=430
        )
        st.markdown(
            """
            <style>
                .stDataFrame {
                    font-size: 14px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )