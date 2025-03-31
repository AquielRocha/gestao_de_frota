import streamlit as st
from app.services.auth import create_user, get_setor_options

def run():
 
    st.markdown("""
    <div style="display: flex; justify-content: center;">
      <div class="login-card">
        <div class="login-title">Crie sua Conta</div>
    """, unsafe_allow_html=True)

    # --- FORMULÁRIO DE CADASTRO (usando st.form) ---
    with st.form("register_form"):
        nome = st.text_input("Nome completo", key="nome_reg")
        email = st.text_input("Email", key="email_reg")
        senha = st.text_input("Senha", type="password", key="senha_reg")

        # Obtém as opções de centro de custo do banco
        setores = get_setor_options()
        if setores:
            setor_selecionado = st.selectbox("Centro de Custo", setores, key="centro_custo_reg")
        else:
            st.warning("Nenhum centro de custo encontrado. Verifique a tabela 'frota'.")
            setor_selecionado = None

        # Botão de envio do formulário
        submit_register = st.form_submit_button("Cadastrar")
        if submit_register:
            if not setor_selecionado:
                st.error("Por favor, selecione um centro de custo válido.")
            else:
                if create_user(nome, email, senha, setor_selecionado):
                    st.success("Usuário criado com sucesso! Agora você já pode fazer login.")
                else:
                    st.error("Este email já está em uso. Tente outro ou faça login.")

    # Botão para voltar ao login
    if st.button("Voltar ao Login"):
        st.session_state.show_registration = False
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
