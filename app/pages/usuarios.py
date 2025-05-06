import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from app.services.auth import check_user_logged_in

# ---------------- DB helpers ----------------

def get_connection():
    return sqlite3.connect("app/database/frota.db", check_same_thread=False)

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

# --------------- CRUD Usuários ---------------

def get_all_users() -> pd.DataFrame:
    sql = """
    SELECT u.id, u.username, u.nome, u.cpf, u.email, u.setor_codigo, u.tipo_usuario,
           s.nome AS setor_nome, s.sigla AS setor_sigla
      FROM usuario u
      LEFT JOIN setor s ON s.codigo = u.setor_codigo
     ORDER BY u.nome;
    """
    with get_connection() as con:
        return pd.read_sql(sql, con)

def create_user(username, nome, cpf, email, senha, setor_codigo, tipo):
    with get_connection() as con:
        con.execute(
            "INSERT INTO usuario (username, nome, cpf, email, senha, setor_codigo, tipo_usuario) VALUES (?,?,?,?,?,?,?)",
            (username, nome, cpf, email, hash_password(senha), setor_codigo, tipo)
        )

def update_user(user_id, username, nome, cpf, email, setor_codigo, tipo, reset_pwd=None):
    cols = "username=?, nome=?, cpf=?, email=?, setor_codigo=?, tipo_usuario=?"
    params = [username, nome, cpf, email, setor_codigo, tipo]
    if reset_pwd:
        cols += ", senha=?"
        params.append(hash_password(reset_pwd))
    params.append(user_id)
    with get_connection() as con:
        con.execute(f"UPDATE usuario SET {cols} WHERE id=?", params)

def delete_user(uid):
    with get_connection() as con:
        adm = con.execute("SELECT tipo_usuario FROM usuario WHERE id=?", (uid,)).fetchone()
        if adm and adm[0] == "admin":
            qtd = con.execute("SELECT COUNT(*) FROM usuario WHERE tipo_usuario='admin'").fetchone()[0]
            if qtd <= 1:
                st.error("Não dá pra excluir o último admin!")
                return
        con.execute("DELETE FROM usuario WHERE id=?", (uid,))

# --------------- CRUD Setores ----------------

def get_all_sectors() -> pd.DataFrame:
    with get_connection() as con:
        return pd.read_sql("SELECT codigo, nome, sigla, cnuc FROM setor ORDER BY nome", con)

def create_sector(nome, sigla, cnuc):
    with get_connection() as con:
        con.execute("INSERT INTO setor (nome, sigla, cnuc) VALUES (?,?,?)", (nome, sigla, cnuc))

def update_sector(cod, nome, sigla, cnuc):
    with get_connection() as con:
        con.execute("UPDATE setor SET nome=?, sigla=?, cnuc=? WHERE codigo=?", (nome, sigla, cnuc, cod))

def delete_sector(cod):
    with get_connection() as con:
        vinc = con.execute("SELECT COUNT(*) FROM usuario WHERE setor_codigo=?", (cod,)).fetchone()[0]
        if vinc:
            st.error("Setor com usuários vinculados não pode ser excluído.")
            return
        con.execute("DELETE FROM setor WHERE codigo=?", (cod,))

# ---------------- Utils ----------------

def chunkify(iterable, n):
    lst = list(iterable)
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def rerun():
    st.rerun()

# ----------- Cards de Usuário ------------

def render_user_card(row: pd.Series):
    uid = int(row.id)
    editing = st.session_state.get("edit_user") == uid

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if editing:
        with st.form(f"form_user_{uid}"):
            col1, col2 = st.columns(2)
            with col1:
                u_username = st.text_input("Username", value=row.username)
                u_nome     = st.text_input("Nome", value=row.nome)
                u_cpf      = st.text_input("CPF", value=row.cpf or "", max_chars=11)
            with col2:
                u_email = st.text_input("Email", value=row.email)
                sectors = get_all_sectors()
                opts    = sectors.codigo.tolist()

                # transforma setor_codigo em int, lidando com bytes/string
                raw = row.setor_codigo
                if isinstance(raw, (bytes, bytearray)):
                    raw = int.from_bytes(raw, "little")
                elif isinstance(raw, str) and raw.isdigit():
                    raw = int(raw)

                idx = opts.index(raw) if pd.notna(raw) and raw in opts else 0
                u_setor = st.selectbox(
                    "Setor",
                    options=opts,
                    index=idx,
                    format_func=lambda x: f"{sectors.loc[sectors.codigo==x,'nome'].values[0]} ({sectors.loc[sectors.codigo==x,'sigla'].values[0]})"
                )
                u_tipo = st.radio("Tipo", ["admin", "comum"], horizontal=True, index=0 if row.tipo_usuario=="admin" else 1)

            st.markdown("**Redefinir senha (opcional)**")
            new_pwd1 = st.text_input("Nova senha", type="password")
            new_pwd2 = st.text_input("Confirmar nova senha", type="password")
            c1, c2 = st.columns([2,1])
            if c1.form_submit_button("💾 Salvar"):
                if new_pwd1 and new_pwd1 != new_pwd2:
                    st.error("Senhas não coincidem.")
                else:
                    update_user(uid, u_username, u_nome, u_cpf, u_email, u_setor, u_tipo, reset_pwd=new_pwd1 or None)
                    st.success("Atualizado.")
                    st.session_state.pop("edit_user", None)
                    rerun()
            if c2.form_submit_button("❌ Cancelar"):
                st.session_state.pop("edit_user", None)
                rerun()
    else:
        st.markdown(f"""
        <div class='card-header'>
          <h2 class='card-title'>{row.nome}</h2>
          <p class='card-sector'>{row.setor_nome} ({row.setor_sigla})</p>
        </div>
        <div class='card-content'>
          <p><strong>Email:</strong> {row.email}</p>
          <p><strong>CPF:</strong> {row.cpf or '-'} | <strong>Tipo:</strong> {row.tipo_usuario}</p>
        </div>
        """, unsafe_allow_html=True)

        ft = st.columns(2)
        if ft[0].button("✏️ Editar", key=f"edit_user_{uid}"):
            st.session_state["edit_user"] = uid
            rerun()
        if ft[1].button("🗑 Excluir", key=f"del_user_{uid}"):
            delete_user(uid)
            st.success("Usuário excluído.")
            rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Cards de Setor -------------

def render_sector_card(row: pd.Series):
    sid = int(row.codigo)
    editing = st.session_state.get("edit_sector") == sid

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if editing:
        with st.form(f"form_sector_{sid}"):
            s_nome = st.text_input("Nome", value=row.nome)
            s_sigla = st.text_input("Sigla", value=row.sigla, max_chars=10)
            s_cnuc = st.text_input("CNUC", value=row.cnuc or "")
            c1, c2 = st.columns([2,1])
            if c1.form_submit_button("💾 Salvar"):
                if not s_nome or not s_sigla:
                    st.error("Preencha todos os campos obrigatórios.")
                else:
                    update_sector(sid, s_nome, s_sigla, s_cnuc)
                    st.session_state.pop("edit_sector", None)
                    st.success("Atualizado.")
                    rerun()
            if c2.form_submit_button("❌ Cancelar"):
                st.session_state.pop("edit_sector", None)
                rerun()
    else:
        st.markdown(f"""
        <div class='card-header'>
          <h2 class='card-title'>{row.nome}</h2>
          <p class='card-sector'>Sigla: {row.sigla}</p>
        </div>
        <div class='card-content'>
          <p><strong>CNUC:</strong> {row.cnuc or '-'}</p>
        </div>
        """, unsafe_allow_html=True)

        ft = st.columns(2)
        if ft[0].button("✏️ Editar", key=f"edit_sector_{sid}"):
            st.session_state["edit_sector"] = sid
            rerun()
        if ft[1].button("🗑 Excluir", key=f"del_sector_{sid}"):
            delete_sector(sid)
            st.success("Setor excluído.")
            rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Dialogs ------------

@st.dialog("Adicionar Novo Usuário")
def dialog_new_user():
    d = st.session_state.setdefault("_new_user", {
        "username": "", "nome": "", "cpf": "", "email": "", "senha": "", "setor": None, "tipo": "comum"
    })
    d["username"] = st.text_input("Username", value=d["username"])
    d["nome"]     = st.text_input("Nome Completo", value=d["nome"])
    d["cpf"]      = st.text_input("CPF", value=d["cpf"], max_chars=11)
    d["email"]    = st.text_input("Email", value=d["email"])
    d["senha"]    = st.text_input("Senha", type="password", value=d["senha"])
    sectors = get_all_sectors()
    opts = sectors.codigo.tolist()
    idx = opts.index(d["setor"]) if d["setor"] in opts else 0
    if opts:
        d["setor"] = st.selectbox(
            "Setor", options=opts, index=idx,
            format_func=lambda x: f"{sectors.loc[sectors.codigo==x,'nome'].values[0]} ({sectors.loc[sectors.codigo==x,'sigla'].values[0]})"
        )
    d["tipo"] = st.radio("Tipo", ["admin", "comum"], horizontal=True, index=0 if d["tipo"] == "admin" else 1)

    if st.button("Salvar Novo Usuário"):
        if not all([d["username"], d["nome"], d["email"], d["senha"], d["setor"]]):
            st.error("Preencha campos obrigatórios.")
        else:
            create_user(d["username"], d["nome"], d["cpf"], d["email"], d["senha"], d["setor"], d["tipo"])
            st.success("Usuário criado!")
            st.session_state.pop("_new_user", None)
            rerun()

@st.dialog("Adicionar Novo Setor")
def dialog_new_sector():
    d = st.session_state.setdefault("_new_sector", {"nome": "", "sigla": "", "cnuc": ""})
    d["nome"]  = st.text_input("Nome", value=d["nome"])
    d["sigla"] = st.text_input("Sigla", value=d["sigla"], max_chars=10)
    d["cnuc"]  = st.text_input("CNUC", value=d["cnuc"])
    if st.button("Salvar Novo Setor"):
        if not d["nome"] or not d["sigla"]:
            st.error("Preencha todos os campos obrigatórios.")
        else:
            create_sector(d["nome"], d["sigla"], d["cnuc"])
            st.success("Setor criado!")
            st.session_state.pop("_new_sector", None)
            rerun()

# ---------- Página Principal ----------

def run():
    check_user_logged_in()
    if st.session_state.user.get("tipo_usuario") != "admin":
        st.error("Acesso só pra administradores.")
        return

    aba_usr, aba_set = st.tabs(["Gestão de Usuários", "Gestão de Setores"])

    # Usuários
    with aba_usr:
        if st.button("➕ Novo Usuário", key="btn_new_user"):
            dialog_new_user()
        search_u = st.text_input("🔍 Pesquisar Usuário", placeholder="Nome, username, email ou CPF")
        mode_u   = st.radio("Exibir como", ["Lista", "Cards"], horizontal=True)
        df_u     = get_all_users()
        if search_u:
            q = search_u.lower()
            df_u = df_u[df_u.apply(lambda r:
                q in str(r.username).lower() or
                q in str(r.nome).lower() or
                q in str(r.email).lower() or
                q in str(r.cpf).lower(), axis=1)]
        if df_u.empty:
            st.info("Nenhum usuário encontrado.")
        elif mode_u == "Lista":
            edit_df = st.data_editor(
                df_u[["id","username","nome","cpf","email","setor_nome","tipo_usuario"]]
                    .rename(columns={"id":"ID","username":"Username","nome":"Nome","cpf":"CPF","email":"Email","setor_nome":"Setor","tipo_usuario":"Tipo"}),
                hide_index=True,
                column_config={"ID": st.column_config.TextColumn(disabled=True),
                               "Tipo": st.column_config.SelectboxColumn(options=["admin","comum"])}
            )
            if st.button("Salvar Alterações (Lista)"):
                for _, r in edit_df.iterrows():
                    s_codigo = df_u[df_u.id == r["ID"]].iloc[0].setor_codigo
                    update_user(r["ID"], r["Username"], r["Nome"], r["CPF"], r["Email"], s_codigo, r["Tipo"])
                st.success("Atualizado!")
                rerun()
        else:
            for chunk in chunkify(df_u.itertuples(), 3):
                cols = st.columns(len(chunk))
                for c, row in zip(cols, chunk):
                    with c:
                        render_user_card(pd.Series(row._asdict()))

    # Setores
    with aba_set:
        if st.button("➕ Novo Setor", key="btn_new_sector"):
            dialog_new_sector()
        search_s = st.text_input("🔍 Pesquisar Setor", placeholder="Nome ou sigla")
        mode_s   = st.radio("Exibir como", ["Lista","Cards"], horizontal=True, key="mode_setor")
        df_s     = get_all_sectors()
        if search_s:
            q = search_s.lower()
            df_s = df_s[df_s.apply(lambda r: q in str(r.nome).lower() or q in str(r.sigla).lower(), axis=1)]
        if df_s.empty:
            st.info("Nenhum setor encontrado.")
        elif mode_s == "Lista":
            edit_df = st.data_editor(
                df_s.rename(columns={"codigo":"Código","nome":"Nome","sigla":"Sigla","cnuc":"CNUC"}),
                hide_index=True,
                column_config={"Código": st.column_config.TextColumn(disabled=True)}
            )
            if st.button("Salvar Alterações (Lista)", key="save_setores"):
                for _, r in edit_df.iterrows():
                    update_sector(r["Código"], r["Nome"], r["Sigla"], r["CNUC"])
                st.success("Atualizado!")
                rerun()
        else:
            for chunk in chunkify(df_s.itertuples(), 3):
                cols = st.columns(len(chunk))
                for c, row in zip(cols, chunk):
                    with c:
                        render_sector_card(pd.Series(row._asdict()))

if __name__ == "__main__":
    run()
