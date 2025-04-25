import streamlit as st
import pandas as pd
import sqlite3
from app.services.auth import check_user_logged_in

# ─────────────────────────────────────────────────────────────────────────────
# Conexão utilitária
# ─────────────────────────────────────────────────────────────────────────────
def get_connection():
    return sqlite3.connect("app/database/frota.db")

# Puxa todos os equipamentos 2025 do setor
def get_equipamentos_2025(setor_codigo: int):
    sql = """
    SELECT *
      FROM equipamentos
     WHERE centro_custo_uc = ?
       AND ano = 2025
    """
    with get_connection() as con:
        df = pd.read_sql(sql, con, params=(setor_codigo,))
    return df

# ─────────────────────────────────────────────────────────────────────────────
# Página
# ─────────────────────────────────────────────────────────────────────────────
def run():
    check_user_logged_in()
    setor_codigo = st.session_state.user["setor_codigo"]

    st.title("📋 Equipamentos (Ano 2025)")

    df = get_equipamentos_2025(setor_codigo)

    if df.empty:
        st.info("Nenhum equipamento 2025 encontrado para este setor.")
        return

    # Remove colunas internas
    df = df.drop(columns=["codigo", "centro_custo_uc"], errors="ignore")

    # Limpa vírgulas em colunas texto
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.replace(",", "", regex=False)

    # Renomeia para títulos mais legíveis
    rename_map = {
        "identificacao":      "Identificação",
        "fabricante":         "Marca",
        "modelo":             "Modelo",
        "ano_fabricacao":     "Ano de Fabricação",
        "ano_modelo":         "Ano do Modelo",
        "cor":                "Cor",
        "tipo_combustivel":   "Combustível",
        "tipo_bem":           "Tipo do Bem",
        "subtipo_bem":        "Subtipo",
        "status":             "Status",
        "observacoes":        "Observação",
        "motorizacao":        "Motorização",
        "tipo_propriedade":   "Tipo de Propriedade",
        "uso_km":             "Uso (km/horas)",
        "data_aquisicao":     "Data Aquisição"
    }
    df = df.rename(columns=rename_map)

    # ───── filtros ─────
    with st.expander("🔎 Filtrar Equipamentos"):
        col1, col2, col3 = st.columns(3)
        tipo = col1.selectbox("Tipo do Bem",
                              ["Todos"] + sorted(df["Tipo do Bem"].dropna().unique()))
        marca = col2.selectbox("Marca",
                               ["Todos"] + sorted(df["Marca"].dropna().unique()))
        modelo = col3.selectbox("Modelo",
                                ["Todos"] + sorted(df["Modelo"].dropna().unique()))

        col4, col5 = st.columns(2)
        status = col4.selectbox("Status",
                                ["Todos"] + sorted(df["Status"].dropna().unique()))
        ano_fab = col5.selectbox("Ano de Fabricação",
                                 ["Todos"] + sorted(df["Ano de Fabricação"].dropna().unique()))

        # aplica filtros
        if tipo != "Todos":
            df = df[df["Tipo do Bem"] == tipo]
        if marca != "Todos":
            df = df[df["Marca"] == marca]
        if modelo != "Todos":
            df = df[df["Modelo"] == modelo]
        if status != "Todos":
            df = df[df["Status"] == status]
        if ano_fab != "Todos":
            df = df[df["Ano de Fabricação"] == ano_fab]

    # ───── tabela ─────
    st.subheader("📑 Equipamentos Homologados e Atualizados!")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={c: st.column_config.Column(label=c) for c in df.columns}
    )

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run()
