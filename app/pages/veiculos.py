import streamlit as st
import pandas as pd
import sqlite3
from app.services.auth import check_user_logged_in

DB = "app/database/frota.db"

# ───────────────────────── helpers ─────────────────────────
def get_connection():
    return sqlite3.connect(DB)

def equipamentos_2025(setor:int) -> pd.DataFrame:
    sql = """
        SELECT *
          FROM equipamentos
         WHERE ano = 2025
           AND centro_custo_uc = ?
    """
    with get_connection() as con:
        return pd.read_sql(sql, con, params=(setor,))

# ───────────────────────── página ─────────────────────────
def run():
    check_user_logged_in()
    setor = st.session_state.user["setor_codigo"]

    st.title("📋 Equipamentos 2025 – Lista Atualizada")

    df = equipamentos_2025(setor)

    if df.empty:
        st.info("Nenhum equipamento de 2025 encontrado para este Centro de Custo.")
        return

    # colunas internas fora
    df = df.drop(columns=["codigo", "centro_custo_uc"], errors="ignore")

    # tira vírgulas de textos
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.replace(",", "", regex=False)

    # renomeia p/ português legível
    df = df.rename(columns={
        "identificacao":    "Identificação",
        "fabricante":       "Marca",
        "modelo":           "Modelo",
        "ano_fabricacao":   "Ano de Fabricação",
        "ano_modelo":       "Ano do Modelo",
        "cor":              "Cor",
        "tipo_combustivel": "Combustível",
        "tipo_bem":         "Tipo do Bem",
        "subtipo_bem":      "Subtipo",
        "status":           "Status",
        "observacoes":      "Observações",
        "motorizacao":      "Motorização",
        "tipo_propriedade": "Tipo de Propriedade",
        "uso_km":           "Uso (km/horas)",
        "data_aquisicao":   "Data de Aquisição"
    })

    # ───────── filtros ─────────
    with st.expander("🔎 Filtros"):
        col1, col2, col3 = st.columns(3)
        tipo   = col1.selectbox("Tipo do Bem",   ["Todos"]+sorted(df["Tipo do Bem"].dropna().unique()))
        marca  = col2.selectbox("Marca",         ["Todos"]+sorted(df["Marca"].dropna().unique()))
        modelo = col3.selectbox("Modelo",        ["Todos"]+sorted(df["Modelo"].dropna().unique()))

        col4, col5 = st.columns(2)
        status  = col4.selectbox("Status",       ["Todos"]+sorted(df["Status"].dropna().unique()))
        ano_fab = col5.selectbox("Ano Fabricação", ["Todos"]+sorted(df["Ano de Fabricação"].dropna().unique()))

        # aplica
        if tipo   != "Todos": df = df[df["Tipo do Bem"]        == tipo]
        if marca  != "Todos": df = df[df["Marca"]              == marca]
        if modelo != "Todos": df = df[df["Modelo"]             == modelo]
        if status != "Todos": df = df[df["Status"]             == status]
        if ano_fab!= "Todos": df = df[df["Ano de Fabricação"]  == ano_fab]

    # ───────── tabela ─────────
    st.markdown("""
        <style>
        .stDataFrame tbody tr:nth-child(odd){background:#f9fafb;}
        .stDataFrame thead tr th{background:#2d3748;color:#fff;}
        </style>
    """, unsafe_allow_html=True)

    st.subheader("📑 Equipamentos Homologados")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=500
    )

# ──────────────────────────────
if __name__ == "__main__":
    run()
