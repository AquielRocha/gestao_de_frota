import streamlit as st
from app.services.auth import create_user, get_setor_options

def run():
    st.title("Registro de Novo Usuário")
    
    nome = st.text_input("Nome completo", key="nome_reg")
    email = st.text_input("Email", key="email_reg")
    senha = st.text_input("Senha", type="password", key="senha_reg")
    
    # Obtém as opções de centro de custo a partir do banco de dados
    setores = get_setor_options()
    if setores:
        setor_selecionado = st.selectbox("Centro de Custo", setores, key="centro_custo_reg")
    else:
        st.warning("Nenhum centro de custo encontrado. Verifique a tabela 'frota'.")
        setor_selecionado = None

    if st.button("Cadastrar", key="btn_cadastrar_reg"):
        if not setor_selecionado:
            st.error("Por favor, selecione um centro de custo válido.")
        else:
            if create_user(nome, email, senha, setor_selecionado):
                st.success("Usuário criado com sucesso! Agora você já pode fazer login.")
            else:
                st.error("Este email já está em uso. Tente outro ou faça login.")
