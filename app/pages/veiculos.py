import streamlit as st
import pandas as pd
import sqlite3
from app.services.auth import check_user_logged_in

# Caminho do banco de dados SQLite
DB = "app/database/frota.db"

# Função para obter conexão com o banco
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)

# Carrega todos os registros da tabela equipamentos para admin
# ou apenas os equipamentos que o usuário atualizou em seu setor
def load_data(user_id: int, setor: int, is_admin: bool) -> pd.DataFrame:
    with get_connection() as con:
        if is_admin:
            sql = "SELECT * FROM equipamentos"
            return pd.read_sql(sql, con)
        # usuário comum: só vê equipamentos que ele atualizou
        codes_sql = "SELECT DISTINCT equipamento_codigo FROM historico_atualizacoes WHERE usuario_id = ?"
        codes = [r[0] for r in con.execute(codes_sql, (user_id,)).fetchall()]
        if not codes:
            return pd.DataFrame(columns=[])  # nenhum equipamento atualizado
        # montar placeholders dinamicamente
        placeholders = ",".join("?" for _ in codes)
        sql = f"SELECT * FROM equipamentos WHERE codigo IN ({placeholders})"
        return pd.read_sql(sql, con, params=codes)

# Página principal
def run():
    check_user_logged_in()
    user = st.session_state.user
    is_admin = user.get("tipo_usuario") == "admin"
    user_id = user.get("id")
    setor = user.get("setor_codigo")

    st.title("📋 Equipamentos")

    df = load_data(user_id, setor, is_admin)
    if df.empty:
        if is_admin:
            st.info("Nenhum equipamento cadastrado.")
        else:
            st.info("Você não atualizou nenhum equipamento neste setor.")
        return

    if is_admin:
        st.subheader("✏️ Modo Admin: edição habilitada")
        edited = st.data_editor(df, use_container_width=True)
        if st.button("💾 Salvar alterações"):
            with get_connection() as con:
                for _, row in edited.iterrows():
                    codigo = row['codigo']
                    cols = [c for c in df.columns if c != 'codigo']
                    set_clause = ", ".join(f"{c}=?" for c in cols)
                    params = [row[c] for c in cols] + [codigo]
                    con.execute(f"UPDATE equipamentos SET {set_clause} WHERE codigo = ?", params)
                con.commit()
            st.success("Alterações salvas com sucesso.")
            st.rerun()
    else:
        st.subheader("👀 Modo Leitura: apenas visualização")
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    run()