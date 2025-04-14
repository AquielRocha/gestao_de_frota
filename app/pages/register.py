import re
import streamlit as st
from app.services.auth import create_user, get_setor_options

def run():
    st.markdown("""
    <div style="display: flex; justify-content: center;">
        <div class="login-title">Crie sua Conta</div>
    """, unsafe_allow_html=True)

    # --- FORMULÁRIO DE CADASTRO ---
    with st.form("register_form"):
        nome = st.text_input("Nome completo", key="nome_reg")
        email = st.text_input("Email", key="email_reg")
        senha = st.text_input("Senha", type="password", key="senha_reg")

        # Carrega os setores e extrai só o nome dentro dos parênteses
        setores_raw = get_setor_options()
        setores_dict = {}  # Mapeia o nome legível para o valor real do banco
        for s in setores_raw:
            match = re.search(r"\(([^)]+)\)", s)
            nome_formatado = match.group(1) if match else s
            setores_dict[nome_formatado] = s

        if setores_dict:
            nome_legivel = list(setores_dict.keys())
            setor_legivel = st.selectbox("Centro de Custo", nome_legivel, key="centro_custo_reg")
            setor_selecionado = setores_dict[setor_legivel]  # Recupera valor original
        else:
            st.warning("Nenhum centro de custo encontrado. Verifique a tabela 'frota'.")
            setor_selecionado = None

        # Botão de envio
        submit_register = st.form_submit_button("Cadastrar")
        if submit_register:
            if not setor_selecionado:
                st.error("Por favor, selecione um centro de custo válido.")
            else:
                if create_user(nome, email, senha, setor_selecionado):
                    st.success("Usuário criado com sucesso! Agora você já pode fazer login.")
                else:
                    st.error("Este email já está em uso. Tente outro ou faça login.")

    # Voltar ao login
    if st.button("Voltar ao Login"):
        st.session_state.show_registration = False
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
