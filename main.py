import streamlit as st
import hydralit_components as hc
from app.services.auth import login_user, get_user_info, create_tables
from app.pages import home, preenchimento, sobre, veiculos
from app.pages import register
import sqlite3

# Configurações iniciais de layout
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

hide_streamlit_style = """
<style>
/* Esconde o menu de navegação, rodapé e cabeçalho padrão do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Remove o espaço padrão (padding superior) do container onde fica o conteúdo */
.block-container {
    padding-top: 0 !important;
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

    if st.session_state.user:
        menu_data = [
            {'icon': "📝", 'label': "Formulário"},
            {'icon': "ℹ️", 'label': "Sobre"},
            {'icon': "🚗", 'label': "Visualizar Equipamentos"},
            {'icon': "🔓", 'label': "Logout"}
        ]
        selected = hc.nav_bar(
            menu_definition=menu_data,
            override_theme={
                'menu_background': '#1f3b4d',
                'txc_inactive': '#FFFFFF',
                'txc_active': '#00c0f2',
                # 'option_active': '#395870',
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
        elif selected == "Sobre":
            sobre.run()
        elif selected == "Visualizar Equipamentos":
            veiculos.run()
        elif selected == "Logout":
            st.session_state.user = None
            st.rerun()
    else:
        if st.session_state.show_registration:
            register.run()
        else:
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
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
