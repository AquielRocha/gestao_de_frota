import streamlit as st
import pandas as pd
import sqlite3
from app.services.auth import check_user_logged_in

# -------------------------------------------------------------------
# Funções de acesso ao banco (SQLite)
# -------------------------------------------------------------------
def get_connection():
    return sqlite3.connect("app/database/veiculos.db")

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, senha_hash, setor_id FROM usuario;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def create_user(nome, email, senha_hash, setor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuario (nome, email, senha_hash, setor_id)
        VALUES (?, ?, ?, ?);
    """, (nome, email, senha_hash, setor_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_user(user_id, nome, email, senha_hash, setor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuario
        SET nome = ?, email = ?, senha_hash = ?, setor_id = ?
        WHERE id = ?;
    """, (nome, email, senha_hash, setor_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuario WHERE id = ?;", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

# -------------------------------------------------------------------
# Função principal da página
# -------------------------------------------------------------------
def run():
    check_user_logged_in()
    usuario_atual = st.session_state.user

    st.title("Gestão de Usuários - Administração")

    # Adição de novo usuário
    st.subheader("Adicionar Novo Usuário")
    with st.expander("Clique para adicionar"):
        novo_nome = st.text_input("Nome")
        novo_email = st.text_input("Email")
        novo_senha = st.text_input("Senha (hash)")
        novo_setor = st.text_input("Setor ID (opcional)")

        if st.button("Criar Usuário"):
            try:
                create_user(novo_nome, novo_email, novo_senha, novo_setor)
                st.success("Usuário criado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao criar usuário: {e}")

    # Carrega todos os usuários
    todos_usuarios = get_all_users()
    df_usuarios = pd.DataFrame(
        todos_usuarios,
        columns=["ID", "Nome", "Email", "SenhaHash", "SetorID"]
    )

    # Filtro de busca
    st.subheader("Lista de Usuários")
    search_text = st.text_input("Buscar por nome ou email")
    if search_text:
        search_lower = search_text.lower()
        df_usuarios = df_usuarios[df_usuarios.apply(
            lambda row: search_lower in str(row["Nome"]).lower() or search_lower in str(row["Email"]).lower(),
            axis=1
        )]

    # Exibição da tabela com edição por linha (experimental)
    st.markdown("#### Tabela de Usuários")
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

    # Formulário para editar usuário selecionado
    st.subheader("Editar Usuário")
    with st.expander("Clique para editar um usuário existente"):
        user_id_editar = st.selectbox("Selecione o ID do usuário", options=df_usuarios["ID"])
        usuario = df_usuarios[df_usuarios["ID"] == user_id_editar].iloc[0]

        nome_edit = st.text_input("Nome", value=usuario["Nome"])
        email_edit = st.text_input("Email", value=usuario["Email"])
        senha_edit = st.text_input("Senha (hash)", value=usuario["SenhaHash"])
        setor_edit = st.text_input("Setor ID", value=usuario["SetorID"])

        if st.button("Salvar Alterações"):
            try:
                update_user(user_id_editar, nome_edit, email_edit, senha_edit, setor_edit)
                st.success("Alterações salvas com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")

    # Excluir usuário
    st.subheader("Excluir Usuário")
    user_id_excluir = st.text_input("Informe o ID do usuário que deseja excluir")
    if st.button("Excluir"):
        if user_id_excluir.strip():
            try:
                delete_user(int(user_id_excluir))
                st.success("Usuário excluído com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao excluir usuário: {e}")
        else:
            st.warning("Por favor, informe um ID válido.")
