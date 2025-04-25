import streamlit as st
import hydralit_components as hc
from app.services.auth import login_user, get_user_info
from app.pages import home, preenchimento, sobre, veiculos, register, usuarios, exportacao

# ------------------------------------------------------------------ #

# -----------------------------------------------------------------------------
# Configurações iniciais de layout
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# -----------------------------------------------------------------------------
# CSS global para esconder elementos do Streamlit e definir estilos básicos
# -----------------------------------------------------------------------------
hide_streamlit_style = """
<style>
/* Esconde o menu padrão, rodapé e cabeçalho */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Remove o padding superior padrão */
.block-container {
    padding-top: 0 !important;
}

/* Estilos para a tela de login */
.login-card {
    background: white;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 350px;
    text-align: center;
}

.login-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
}

.login-sub {
    font-size: 14px;
    margin-bottom: 20px;
    color: #666;
}

.login-hr {
    border: none;
    border-top: 1px solid #eee;
    margin: 20px 0;
}

.login-text-center {
    font-size: 14px;
    color: #666;
}

/* Estilização dos botões */
button[kind] {
    border: none;
    border-radius: 27px;
    padding: 10px 20px;
    background-color: blue;
    color: white;
    font-weight: bold;
    cursor: pointer;
    margin-top: 10px;
}
button[kind]:hover {
    background-color: #0056b3;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Função principal (main) - Lógica de Login e Navegação

# ------------------------------------------------------------------ #
def main():
    # ---------- sessão ----------
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("show_registration", False)

    # ---------- user logado ----------
    if st.session_state.user:
        menu_data = [
            {'icon': "📝", 'label': "Formulário"},
            {'icon': "🚗", 'label': "Visualizar Equipamentos"},
            {'icon': "📤", 'label': "Exportação"},
            {'icon': "ℹ️", 'label': "Sobre"},
            {'icon': "👤", 'label': "Usuários"},
            {'icon': "🔓", 'label': "Logout"}
        ]
        choice = hc.nav_bar(
            menu_definition=menu_data,
            override_theme={
                'menu_background': '#1f3b4d',
                'txc_inactive': '#FFFFFF',
                'txc_active': '#00c0f2'
            },
            home_name='Home',
            sticky_nav=True,
            sticky_mode='pinned',
            hide_streamlit_markers=True
        )

        if choice == "Home":
            home.run()
        elif choice == "Formulário":
            preenchimento.run()
        elif choice == "Exportação":
            exportacao.run()
        elif choice == "Sobre":
            sobre.run()
        elif choice == "Visualizar Equipamentos":
            veiculos.run()
        elif choice == "Usuários":
            usuarios.run()
        elif choice == "Logout":
            st.session_state.user = None
            st.rerun()

    # ---------- login / registro ----------
    else:
        if st.session_state.show_registration:
            register.run()
            return

        # ----- tela de login -----
        st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
        st.markdown("<div class='login-title'>Bem-vindo(a)!</div>",
                    unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Gerencie seus veículos e equipamentos sem estresse.</div>",
                    unsafe_allow_html=True)

        with st.form("login_form"):
            cpf = st.text_input("CPF (só números)", key="login_cpf", max_chars=11)
            senha = st.text_input("Senha", type="password", key="login_senha")
            entrou = st.form_submit_button("Entrar")

        if entrou:
            if login_user(cpf, senha):
                st.session_state.user = get_user_info(cpf)
                st.rerun()
            else:
                st.error("CPF ou senha errados, parceiro.")

        st.markdown("<hr class='login-hr'/>", unsafe_allow_html=True)
        st.markdown("<p class='login-text-center'>Não possui conta?</p>",
                    unsafe_allow_html=True)

        if st.button("Criar Conta", key="btn_register"):
            st.session_state.show_registration = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
