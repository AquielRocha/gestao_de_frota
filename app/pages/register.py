import streamlit as st
from app.services.auth import create_user, get_setor_options

def run():
    # Podemos reutilizar o mesmo estilo que usamos na tela de login
    # Caso já tenha sido definido no main, ele continuará valendo.
    # Mas, se quiser garantir, podemos repetir aqui (ou criar um "load_css()" comum).
    st.markdown("""
        <style>
        /* Fundo em gradiente (opcional, se já estiver no main.py não precisa repetir) */
        .stApp {
            background: linear-gradient(135deg, #E8F0F8 0%, #FFFFFF 100%);
        }

        .block-container {
            padding: 0rem 1rem;
        }

        /* Card principal para cadastro */
        .login-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            width: 100%;
            max-width: 500px; /* um pouco mais largo que o login */
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }

        /* Título do card */
        .login-title {
            text-align: center;
            font-weight: 700;
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 1rem;
        }

        /* Linha divisória estilizada */
        .login-hr {
            border: none;
            height: 1px;
            background: linear-gradient(to right, #ccc, #999, #ccc);
            margin: 1rem 0;
        }

        /* Texto centralizado */
        .login-text-center {
            text-align: center;
            margin-top: 1rem;
        }

        /* Botão gradiente */
        .gradient-button {
            background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
            border: none;
            color: #fff;
            padding: 0.6rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            margin-top: 1rem;
        }
        .gradient-button:hover {
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)

    # Centraliza o "card" no meio da página
    st.markdown("""
    <div style="display: flex; justify-content: center;">
      <div class="login-card">
        <div class="login-title">Crie sua Conta</div>
    """, unsafe_allow_html=True)

    # Aqui começa o formulário de cadastro
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

    # Botão de cadastro (usando CSS de classe .gradient-button)
    if st.button("Cadastrar", key="btn_cadastrar_reg"):
        if not setor_selecionado:
            st.error("Por favor, selecione um centro de custo válido.")
        else:
            if create_user(nome, email, senha, setor_selecionado):
                st.success("Usuário criado com sucesso! Agora você já pode fazer login.")
            else:
                st.error("Este email já está em uso. Tente outro ou faça login.")

    # Fecha a div do card
    st.markdown("</div></div>", unsafe_allow_html=True)
