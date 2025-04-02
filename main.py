import streamlit as st
import hydralit_components as hc
from app.services.auth import login_user, get_user_info, create_tables
from app.pages import home, preenchimento, sobre, veiculos, register
import sqlite3
import base64
from pathlib import Path
from app.pages import exportacao

# Configurações iniciais de layout
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# CSS global para esconder elementos do Streamlit e definir estilos básicos
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
    border-radius: 4px;
    padding: 10px 20px;
    background-color: #007BFF;
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

# Inicializa as tabelas
create_tables()

# Inserir dados de exemplo se necessário
def insert_dummy_frota():
    conn = sqlite3.connect("app/database/veiculos.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM frota")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany("""
            INSERT INTO frota (centro_custo, placa, modelo) 
            VALUES (?, ?, ?)
        """, [
            ("Setor A", "ABC-1234", "Modelo X"),
            ("Setor B", "DEF-5678", "Modelo Y"),
            ("Setor A", "GHI-9012", "Modelo Z")
        ])
        conn.commit()
    conn.close()

insert_dummy_frota()

def main():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "show_registration" not in st.session_state:
        st.session_state.show_registration = False

    # Se o usuário já estiver logado, exibe o menu principal
    if st.session_state.user:
        menu_data = [
            {'icon': "📝", 'label': "Formulário"},
            {'icon': "🚗", 'label': "Visualizar Equipamentos"},
            {'icon': "📤", 'label': "Exportação"},
            {'icon': "ℹ️", 'label': "Sobre"},
            {'icon': "🔓", 'label': "Logout"}
        ]
        selected = hc.nav_bar(
            menu_definition=menu_data,
            override_theme={
                'menu_background': '#1f3b4d',
                'txc_inactive': '#FFFFFF',
                'txc_active': '#00c0f2',
            },
            home_name='Home',
            sticky_nav=True,
            sticky_mode='pinned',
            hide_streamlit_markers=True
        )
        if selected == "Home":
            home.run()
        elif selected == "Formulário":
            preenchimento.run()
        elif selected == "Exportação":
            exportacao.run()
        elif selected == "Sobre":
            sobre.run()
        elif selected == "Visualizar Equipamentos":
            veiculos.run()
        elif selected == "Logout":
            st.session_state.user = None
            st.rerun()
    else:
        # Se estiver na tela de registro, chama a função do register
        if st.session_state.show_registration:
            register.run()
        else:
            # Tela de login com HTML/CSS
            with st.container():
                st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
                st.markdown("<div class='login-title'>Bem-vindo(a)!</div>", unsafe_allow_html=True)
                st.markdown("<div class='login-sub'>Gerencie de forma prática e eficiente todos os seus veículos e equipamentos.</div>", unsafe_allow_html=True)
                
                with st.form("login_form"):
                    email = st.text_input("Email", key="login_email")
                    senha = st.text_input("Senha", type="password", key="login_senha")
                    if st.form_submit_button("Entrar"):
                        if login_user(email, senha):
                            st.session_state.user = get_user_info(email)
                            st.rerun()
                        else:
                            st.error("Credenciais inválidas!")
                
                st.markdown("<hr class='login-hr'/>", unsafe_allow_html=True)
                st.markdown("<p class='login-text-center'>Não possui conta?</p>", unsafe_allow_html=True)
                if st.button("Criar Conta", key="btn_register"):
                    st.session_state.show_registration = True
                    st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
