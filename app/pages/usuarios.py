import streamlit as st
import pandas as pd
import sqlite3
from st_aggrid import AgGrid, GridOptionsBuilder
from app.services.auth import check_user_logged_in

# -------------------------------------------------------------------
# Funções de acesso ao banco (SQLite)
# -------------------------------------------------------------------
def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect("app/database/veiculos.db")
    return conn

def get_all_users():
    """
    Retorna todos os usuários da tabela `usuario`.
    Estrutura esperada (id, nome, email, senha_hash, setor_id).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, senha_hash, setor_id FROM usuario;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def create_user(nome, email, senha_hash, setor_id):
    """Cria um novo usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO usuario (nome, email, senha_hash, setor_id)
        VALUES (?, ?, ?, ?);
        """,
        (nome, email, senha_hash, setor_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def update_user(user_id, nome, email, senha_hash, setor_id):
    """Atualiza os dados de um usuário específico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuario
        SET nome = ?, email = ?, senha_hash = ?, setor_id = ?
        WHERE id = ?;
        """,
        (nome, email, senha_hash, setor_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_user(user_id):
    """Exclui um usuário específico."""
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
    """
    Executa a tela de gestão de usuários.
    Deve ser chamada em algum ponto do seu app principal.
    """
    # Garante que o usuário está logado
    check_user_logged_in()
    usuario_atual = st.session_state.user  # Dicionário com info do usuário logado

    # Se você quiser restringir somente a alguns usuários,
    # você pode colocar checagens aqui. Por enquanto, está livre.
    # Exemplo (comentado):
    # if usuario_atual.get("perfil") != "admin":
    #     st.error("Acesso negado. Somente administradores podem acessar esta página.")
    #     return

    st.title("Gestão de Usuários - Administração")

    # Carrega todos os usuários da tabela `usuario`
    todos_usuarios = get_all_users()  # lista de tuplas: (id, nome, email, senha_hash, setor_id)

    # ~~~~~~~~~~~~~~~~ Interface para inserir um novo usuário ~~~~~~~~~~~~~~~~~
    st.subheader("Adicionar Novo Usuário")
    with st.expander("Clique para adicionar"):
        novo_nome = st.text_input("Nome", key="novo_nome")
        novo_email = st.text_input("Email", key="novo_email")
        novo_senha = st.text_input("Senha (hash)", key="novo_senha")
        novo_setor = st.text_input("Setor ID (opcional)", key="novo_setor")
        
        if st.button("Criar Usuário"):
            try:
                create_user(novo_nome, novo_email, novo_senha, novo_setor)
                st.success("Usuário criado com sucesso!")
                st.rerun()  # Recarrega a página para mostrar o usuário criado
            except Exception as e:
                st.error(f"Erro ao criar usuário: {e}")

    # ~~~~~~~~~~~~~~~~ Filtro de pesquisa simples ~~~~~~~~~~~~~~~~~
    st.subheader("Lista de Usuários")
    search_text = st.text_input("Buscar por nome ou email", key="busca")

    if search_text:
        search_lower = search_text.lower()
        usuarios_filtrados = [
            u for u in todos_usuarios
            if search_lower in u[1].lower() or search_lower in u[2].lower()
        ]
    else:
        usuarios_filtrados = todos_usuarios

    # ~~~~~~~~~~~~~~~~ Exibição em tabela editável (st_aggrid) ~~~~~~~~~~~~~~~~~
    # Converte para DataFrame para ficar mais fácil manipular no AgGrid
    df_usuarios = pd.DataFrame(
        usuarios_filtrados,
        columns=["ID", "Nome", "Email", "SenhaHash", "SetorID"]
    )

    st.markdown("#### Tabela de Usuários (editável)")
    gb = GridOptionsBuilder.from_dataframe(df_usuarios)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    # Permite edição de colunas, exceto o ID
    gb.configure_column("ID", editable=False)
    gb.configure_column("Nome", editable=True)
    gb.configure_column("Email", editable=True)
    gb.configure_column("SenhaHash", header_name="Senha (hash)", editable=True)
    gb.configure_column("SetorID", header_name="Setor (ID)", editable=True)

    gridOptions = gb.build()
    grid_return = AgGrid(
        df_usuarios,
        gridOptions=gridOptions,
        update_mode='MODEL_CHANGED',
        theme="streamlit"
    )

    # Se o usuário editar alguma linha, vamos capturar as alterações
    df_editado = grid_return["data"]  # DataFrame resultante

    # Botão para salvar alterações
    if st.button("Salvar Alterações"):
        try:
            for idx, row in df_editado.iterrows():
                user_id = row["ID"]
                update_user(
                    user_id=user_id,
                    nome=row["Nome"],
                    email=row["Email"],
                    senha_hash=row["SenhaHash"],
                    setor_id=row["SetorID"]
                )
            st.success("Alterações salvas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar alterações: {e}")

    # ~~~~~~~~~~~~~~~~ Excluir usuário ~~~~~~~~~~~~~~~~~
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
