import streamlit as st
import pandas as pd
import sqlite3, hashlib
from app.services.auth import check_user_logged_in

# ──────────────────────────────────────────────────────────────────────────────
# Conexão
# ──────────────────────────────────────────────────────────────────────────────
def get_connection():
    return sqlite3.connect("app/database/frota.db")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────────────────────────────────────
def get_all_users() -> pd.DataFrame:
    sql = """
    SELECT u.id, u.username, u.nome, u.cpf, u.email,
           u.setor_codigo,
           u.tipo_usuario,
           s.nome  AS setor_nome,
           s.sigla AS setor_sigla
      FROM usuario u
 LEFT JOIN setor   s ON s.codigo = u.setor_codigo
    ORDER BY u.nome;
    """
    with get_connection() as con:
        return pd.read_sql(sql, con)


def get_all_sectors() -> pd.DataFrame:
    with get_connection() as con:
        return pd.read_sql("SELECT codigo, nome, sigla FROM setor ORDER BY nome", con)


def create_user(username, nome, cpf, email, senha, setor_codigo, tipo):
    sql = """
    INSERT INTO usuario (username, nome, cpf, email, senha, setor_codigo, tipo_usuario)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as con:
        con.execute(sql, (
            username, nome, cpf, email,
            hash_password(senha), setor_codigo, tipo
        ))


def update_user(user_id, username, nome, cpf, email,
                setor_codigo, tipo, reset_password=None):
    cols = "username=?, nome=?, cpf=?, email=?, setor_codigo=?, tipo_usuario=?"
    params = [username, nome, cpf, email, setor_codigo, tipo]
    if reset_password:
        cols += ", senha=?"
        params.append(hash_password(reset_password))
    params.append(user_id)

    sql = f"UPDATE usuario SET {cols} WHERE id=?"
    with get_connection() as con:
        con.execute(sql, params)


def delete_user(user_id):
    with get_connection() as con:
        cur = con.execute("SELECT tipo_usuario FROM usuario WHERE id=?", (user_id,))
        tipo = cur.fetchone()[0]

        if tipo == "admin":
            qtd = con.execute(
                "SELECT COUNT(*) FROM usuario WHERE tipo_usuario='admin'"
            ).fetchone()[0]
            if qtd <= 1:
                st.error("Não dá pra excluir o último admin!")
                return
        con.execute("DELETE FROM usuario WHERE id=?", (user_id,))


def create_sector(nome, sigla):
    with get_connection() as con:
        con.execute("INSERT INTO setor (nome, sigla) VALUES (?, ?)", (nome, sigla))


def update_sector(cod, nome, sigla):
    with get_connection() as con:
        con.execute("UPDATE setor SET nome=?, sigla=? WHERE codigo=?", (nome, sigla, cod))


def delete_sector(cod):
    with get_connection() as con:
        vinc = con.execute(
            "SELECT COUNT(*) FROM usuario WHERE setor_codigo=?", (cod,)
        ).fetchone()[0]
        if vinc:
            st.error("Setor com usuários vinculados não pode ser excluído.")
            return
        con.execute("DELETE FROM setor WHERE codigo=?", (cod,))


# ──────────────────────────────────────────────────────────────────────────────
# Página
# ──────────────────────────────────────────────────────────────────────────────
def run():
    check_user_logged_in()
    usr = st.session_state.user
    if usr["tipo_usuario"] != "admin":
        st.error("Acesso só pra administradores.")
        return

    st.title("📋 Administração do Sistema")
    aba_usr, aba_set = st.tabs(["Gestão de Usuários", "Gestão de Setores"])

    # ════════════════════════════════════════════════════════════════════════
    # 1) GESTÃO DE USUÁRIOS
    # ════════════════════════════════════════════════════════════════════════
    with aba_usr:
        st.header("👥 Gestão de Usuários")

        # ───── Criação ─────
        with st.expander("➕ Novo usuário"):
            with st.form("add_user"):
                col1, col2 = st.columns(2)
                with col1:
                    n_user = st.text_input("Username*")
                    n_nome = st.text_input("Nome*")
                    n_cpf  = st.text_input("CPF")
                with col2:
                    n_email = st.text_input("Email*")
                    s1 = st.text_input("Senha*", type="password")
                    s2 = st.text_input("Confirme a senha*", type="password")

                sectors_df = get_all_sectors()
                options_setor = [int(x) for x in sectors_df["codigo"]]
                set_sel = st.selectbox(
                    "Setor",
                    options=options_setor,
                    format_func=lambda x: f"{sectors_df.loc[sectors_df.codigo == x, 'nome'].values[0]} "
                                          f"({sectors_df.loc[sectors_df.codigo == x, 'sigla'].values[0]})"
                )
                tipo_sel = st.radio("Tipo", ["admin", "comum"], horizontal=True)

                if st.form_submit_button("Criar"):
                    if not all([n_user, n_nome, n_email, s1, s2]):
                        st.error("Preencha todos os campos obrigatórios.")
                    elif s1 != s2:
                        st.error("As senhas não coincidem.")
                    else:
                        try:
                            create_user(n_user, n_nome, n_cpf, n_email, s1, set_sel, tipo_sel)
                            st.success("Usuário criado.")
                            st.rerun()
                        except sqlite3.IntegrityError as e:
                            st.error(f"Erro: {e}")

        # ───── Listagem / edição ─────
        filtro = st.text_input("🔍 Filtrar por nome, user ou email")
        df_u = get_all_users()
        if filtro:
            f = filtro.lower()
            df_u = df_u[
                df_u.nome.str.lower().str.contains(f) |
                df_u.username.str.lower().str.contains(f) |
                df_u.email.str.lower().str.contains(f)
            ]

        if df_u.empty:
            st.info("Nenhum usuário encontrado.")
        else:
            show = df_u.copy()
            show["setor"] = show["setor_nome"] + " (" + show["setor_sigla"] + ")"
            show = show[["id", "username", "nome", "email", "tipo_usuario", "setor"]]
            show.columns = ["ID", "Username", "Nome", "Email", "Tipo", "Setor"]

            sel = st.selectbox(
                "Escolha para editar",
                options=show.ID,
                format_func=lambda x: f"{show.loc[show.ID == x, 'Nome'].values[0]} (ID {x})"
            )

            u = df_u[df_u.id == sel].iloc[0]

            with st.expander(f"✏️ Editar {u.nome}", True):
                with st.form("edit_user"):
                    ce1, ce2 = st.columns(2)
                    with ce1:
                        e_user = st.text_input("Username", value=u.username)
                        e_nome = st.text_input("Nome", value=u.nome)
                        e_cpf  = st.text_input("CPF", value=u.cpf or "")
                    with ce2:
                        e_email = st.text_input("Email", value=u.email)

                        sect_df = get_all_sectors()
                        options_setor = [int(x) for x in sect_df["codigo"]]
                        idx = options_setor.index(int(u.setor_codigo)) if pd.notna(u.setor_codigo) and int(u.setor_codigo) in options_setor else 0
                        e_set = st.selectbox(
                            "Setor",
                            options=options_setor,
                            index=idx,
                            format_func=lambda x: f"{sect_df.loc[sect_df.codigo == x, 'nome'].values[0]} "
                                                  f"({sect_df.loc[sect_df.codigo == x, 'sigla'].values[0]})"
                        )
                        e_tipo = st.radio("Tipo", ["admin", "comum"],
                                          index=0 if u.tipo_usuario == "admin" else 1,
                                          horizontal=True)

                    st.markdown("***Redefinir senha (opcional)***")
                    p1 = st.text_input("Nova senha", type="password")
                    p2 = st.text_input("Confirmar nova senha", type="password")

                    c_salvar, c_del = st.columns(2)
                    if c_salvar.form_submit_button("💾 Salvar"):
                        if p1 and p1 != p2:
                            st.error("Senhas não coincidem.")
                        else:
                            update_user(u.id, e_user, e_nome, e_cpf,
                                        e_email, e_set, e_tipo,
                                        reset_password=p1 if p1 else None)
                            st.success("Atualizado.")
                            st.rerun()

                    if c_del.form_submit_button("❌ Excluir"):
                        delete_user(u.id)
                        st.success("Usuário excluído.")
                        st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # 2) GESTÃO DE SETORES
    # ════════════════════════════════════════════════════════════════════════
    with aba_set:
        st.header("🏢 Gestão de Setores")

        # ───── criar setor ─────
        with st.expander("➕ Novo setor"):
            with st.form("add_sector"):
                n_nome = st.text_input("Nome*")
                n_sigla = st.text_input("Sigla*", max_chars=10)
                if st.form_submit_button("Criar setor"):
                    if not n_nome or not n_sigla:
                        st.error("Preencha todos os campos obrigatórios.")
                    else:
                        try:
                            create_sector(n_nome, n_sigla)
                            st.success("Setor criado.")
                            st.rerun()
                        except sqlite3.IntegrityError as e:
                            st.error(f"Erro: {e}")

        # ───── listagem / edição ─────
        sect_df = get_all_sectors()
        sfiltro = st.text_input("🔍 Filtrar setor por nome ou sigla")
        if sfiltro:
            f = sfiltro.lower()
            sect_df = sect_df[
                sect_df.nome.str.lower().str.contains(f) |
                sect_df.sigla.str.lower().str.contains(f)
            ]

        if sect_df.empty:
            st.info("Nenhum setor encontrado.")
        else:
            opc_set = [int(x) for x in sect_df.codigo]
            sel_set = st.selectbox(
                "Escolha para editar",
                options=opc_set,
                format_func=lambda x: f"{sect_df.loc[sect_df.codigo == x, 'nome'].values[0]} "
                                      f"({sect_df.loc[sect_df.codigo == x, 'sigla'].values[0]})"
            )
            s = sect_df[sect_df.codigo == sel_set].iloc[0]

            with st.expander(f"✏️ Editar {s.nome}", True):
                with st.form("edit_sector"):
                    e_nome = st.text_input("Nome", value=s.nome)
                    e_sigla = st.text_input("Sigla", value=s.sigla, max_chars=10)

                    cs, cd = st.columns(2)
                    if cs.form_submit_button("💾 Salvar"):
                        if not e_nome or not e_sigla:
                            st.error("Preencha ambos campos.")
                        else:
                            update_sector(s.codigo, e_nome, e_sigla)
                            st.success("Atualizado.")
                            st.rerun()

                    if cd.form_submit_button("❌ Excluir"):
                        delete_sector(s.codigo)
                        st.success("Setor excluído.")
                        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run()
