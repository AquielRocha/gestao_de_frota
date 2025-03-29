import streamlit as st
import hydralit_components as hc
from app.services.auth import login_user, get_user_info, create_tables
from app.pages import home, preenchimento, sobre, register, veiculos
import sqlite3

# Tentativa de usar lottie (opcional). Para usar, descomente e instale streamlit-lottie:
# from streamlit_lottie import st_lottie

# Configurações iniciais de layout
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# Esconde o menu default do Streamlit e o rodapé
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Remove padding extra */
    .block-container {
        padding: 0rem 1rem;
    }

    /* Fundo em gradiente para a página toda */
    .stApp {
        background: linear-gradient(135deg, #E8F0F8 0%, #FFFFFF 100%);
    }

    /* Card principal */
    .login-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 2rem;
        width: 100%;
        max-width: 400px;
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

    /* Divisória estilizada */
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
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Inicializa as tabelas (incluindo 'usuario' e 'frota')
create_tables()

# (Opcional) Insere dados de exemplo na tabela 'frota'
def insert_dummy_frota():
    conn = sqlite3.connect("app/database/veiculos.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM frota")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO frota (centro_custo, placa, modelo) VALUES (?, ?, ?)", ("Setor A", "ABC-1234", "Modelo X"))
        cursor.execute("INSERT INTO frota (centro_custo, placa, modelo) VALUES (?, ?, ?)", ("Setor B", "DEF-5678", "Modelo Y"))
        cursor.execute("INSERT INTO frota (centro_custo, placa, modelo) VALUES (?, ?, ?)", ("Setor A", "GHI-9012", "Modelo Z"))
        conn.commit()
    conn.close()

insert_dummy_frota()

def main():
    # Inicializa a variável de sessão para o usuário
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        # Navbar (quando logado)
        menu_data = [
            {'icon': "🏠", 'label': "Home"},
            {'icon': "📝", 'label': "Formulário"},
            {'icon': "ℹ️", 'label': "Sobre"},
            {'icon': "🚗", 'label': "Visualizar Equipamentos"},
            {'icon': "🔓", 'label': "Logout"}
        ]

        over_theme = {
            'menu_background': '#1f3b4d',  
            'txc_inactive': '#FFFFFF',    
            'txc_active': '#00c0f2',      
            'option_active': '#395870',   
        }

        selected = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,
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
        # Layout do login em duas colunas:
        col_left, col_right = st.columns(2)

        # (Opcional) Imagem ou lottie do lado esquerdo
        with col_left:
            st.markdown("<br><br><br>", unsafe_allow_html=True)  # Espaço extra
            st.markdown("""
                <h1 style="font-size:2.5rem; margin-top: 2rem; color: #333;">
                  Bem-vindo(a)!
                </h1>
                <p style="font-size:1.1rem; margin-bottom: 2rem; color: #555; max-width: 80%;">
                  Gerencie de forma prática e eficiente todos os seus veículos e equipamentos. 
                  Faça login para continuar.
                </p>
            """, unsafe_allow_html=True)

            # Se quiser usar lottie animation
            # lottie_json = ... # Carregue seu JSON
            # st_lottie(lottie_json, height=300)

        # Card de Login na coluna da direita
        with col_right:
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            st.markdown("<div class='login-title'>Acesso ao Sistema</div>", unsafe_allow_html=True)

            email = st.text_input("Email", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_senha")

            # Botão de Login com CSS gradiente
            if st.button("Entrar", key="btn_login", help="Clique para entrar"):
                if login_user(email, senha):
                    user_info = get_user_info(email)
                    st.session_state.user = user_info
                    st.rerun()
                else:
                    st.error("Credenciais inválidas!")

            st.markdown("<hr class='login-hr'/>", unsafe_allow_html=True)
            st.markdown("<p class='login-text-center'>Não possui conta? Cadastre-se abaixo:</p>", unsafe_allow_html=True)

            # Botão "Criar Conta" também com estilo gradiente
            if st.button("Criar Conta", key="btn_register"):
                register.run()

            st.markdown("</div>", unsafe_allow_html=True)  # Fecha o card

if __name__ == "__main__":
    main()
