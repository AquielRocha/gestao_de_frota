import streamlit as st
import pandas as pd
import sqlite3
from app.services.auth import check_user_logged_in

DB = "app/database/frota.db"

# ───────── helpers ─────────
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)

def equipamentos_2025(setor: int = None) -> pd.DataFrame:
    """
    Retorna todos equipamentos de 2025 (se setor=None, traz tudo para admin)
    e adiciona coluna created_by vinda da primeira inserção no histórico.
    """
    sql = """
        SELECT
          e.*,
          (
            SELECT h.usuario_id
              FROM historico_atualizacoes h
             WHERE h.equipamento_codigo = e.codigo
               AND h.acao = 'insercao'
             ORDER BY h.data_atualizacao
             LIMIT 1
          ) AS created_by
        FROM equipamentos e
       WHERE e.ano = 2025
    """
    params = []
    if setor is not None:
        sql += " AND e.centro_custo_uc = ?"
        params.append(setor)
    with get_connection() as con:
        return pd.read_sql(sql, con, params=params)

# ───────── aplicador de updates ─────────
def _apply_updates(df_edited: pd.DataFrame, is_admin: bool):
    user = st.session_state.user
    user_id = user["id"]
    now = pd.Timestamp.now()
    with get_connection() as con:
        for _, row in df_edited.iterrows():
            codigo = row["codigo"]
            created_by = row.get("created_by")
            # se não for admin e não for dono, ignora
            if not is_admin and created_by != user_id:
                continue

            # monta cláusula SET com todas colunas exceto chaves e metadados
            cols = [
                c for c in df_edited.columns
                if c not in ("codigo", "centro_custo_uc", "ano", "created_by")
            ]
            set_clause = ", ".join(f"{c}=?" for c in cols)
            params = [row[c] for c in cols] + [codigo]
            con.execute(f"UPDATE equipamentos SET {set_clause} WHERE codigo = ?", params)

            # registra no histórico
            detalhes = "; ".join(f"{c}={row[c]}" for c in cols)
            con.execute(
                """
                INSERT INTO historico_atualizacoes
                  (usuario_id, equipamento_codigo, data_atualizacao, acao, detalhes)
                VALUES (?,?,?,?,?)
                """,
                (user_id, codigo, now, "atualizacao", detalhes)
            )
        con.commit()

# ───────── página ─────────
def run():
    check_user_logged_in()
    user = st.session_state.user
    is_admin = user.get("tipo_usuario") == "admin"
    user_setor = None if is_admin else user["setor_codigo"]
    user_id = user["id"]

    st.title("📋 Equipamentos 2025 – Lista Atualizada")

    # busca dados
    df = equipamentos_2025(user_setor)
    if df.empty:
        st.info("Nenhum equipamento de 2025 encontrado.")
        return

    # prepara display: limpa vírgulas e renomeia colunas
    df_display = df.drop(columns=["centro_custo_uc"], errors="ignore").copy()
    for col in df_display.select_dtypes(include="object"):
        df_display[col] = df_display[col].str.replace(",", "", regex=False)
    df_display = df_display.rename(columns={
        "codigo":           "Código",
        "usuario_id":       "Criado por",
        "created_by":       "Criado por (original)",
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

    # filtros
    with st.expander("🔎 Filtros"):
        c1, c2, c3 = st.columns(3)
        tipo   = c1.selectbox("Tipo do Bem",   ["Todos"] + sorted(df_display["Tipo do Bem"].dropna().unique()))
        marca  = c2.selectbox("Marca",         ["Todos"] + sorted(df_display["Marca"].dropna().unique()))
        modelo = c3.selectbox("Modelo",        ["Todos"] + sorted(df_display["Modelo"].dropna().unique()))
        c4, c5 = st.columns(2)
        status  = c4.selectbox("Status",       ["Todos"] + sorted(df_display["Status"].dropna().unique()))
        ano_fab = c5.selectbox("Ano Fabricação", ["Todos"] + sorted(df_display["Ano de Fabricação"].dropna().unique()))

        if tipo   != "Todos": df_display = df_display[df_display["Tipo do Bem"]      == tipo]
        if marca  != "Todos": df_display = df_display[df_display["Marca"]            == marca]
        if modelo != "Todos": df_display = df_display[df_display["Modelo"]           == modelo]
        if status != "Todos": df_display = df_display[df_display["Status"]           == status]
        if ano_fab!= "Todos": df_display = df_display[df_display["Ano de Fabricação"]== ano_fab]

    st.subheader("📑 Equipamentos 2025")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=300)

    # edição
    if is_admin:
        st.subheader("✏️ Edição (Admin)")
        edited = st.data_editor(
            df, hide_index=True,
            column_config={c: st.column_config.TextColumn() for c in df.columns}
        )
        if st.button("💾 Salvar alterações (Admin)"):
            _apply_updates(edited, is_admin=True)
            st.success("Atualizado como Admin.")
            st.experimental_rerun()
    else:
        st.subheader("✏️ Edição (Seus registros)")
        df_user = df[df["created_by"] == user_id]
        if df_user.empty:
            st.info("Você não criou nenhum equipamento em 2025.")
        else:
            edited = st.data_editor(
                df_user, hide_index=True,
                column_config={c: st.column_config.TextColumn() for c in df_user.columns}
            )
            if st.button("💾 Salvar suas alterações"):
                _apply_updates(edited, is_admin=False)
                st.success("Seus registros foram atualizados.")
                st.experimental_rerun()

if __name__ == "__main__":
    run()
