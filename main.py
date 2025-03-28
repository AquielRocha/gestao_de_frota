import streamlit as st
import hydralit_components as hc
from app.services.auth import login_user, get_user_info, create_tables
from app.pages import home, preenchimento, sobre, register, veiculos


st.set_page_config(layout='wide',initial_sidebar_state='collapsed',)

# Esconde o cabeçalho (menu) e rodapé padrão do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Inicializa as tabelas (incluindo 'usuario' e 'frota')
create_tables()

# (Opcional) Inserir dados dummy na tabela 'frota' se estiver vazia:
def insert_dummy_frota():
    import sqlite3
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
    
    # Inicializa a variável de sessão para o usuário, se ainda não existir
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        # Define os itens do menu para a navbar utilizando hydralit_components
        menu_data = [
            {'icon': "📝", 'label': "Formulário"},
            {'icon': "ℹ️", 'label': "Sobre"},
            {'icon': "🚗", 'label': "Visualizar Equipamentos"},
            {'icon': "🔓", 'label': "Logout"}
        ]

        # Exemplo de customização do tema (opcional)
        over_theme = {
            'txc_inactive': '#FFFFFF',    # Cor do texto inativo
            'menu_background': '#0E1117',   # Cor de fundo da navbar
            'txc_active': '#00c0f2',        # Cor do texto quando ativo
        }

        # Renderiza a navbar personalizada utilizando o modo "Pinned"
        # Aqui, sticky_mode está definido como 'pinned'
        selected = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,  # Se desejar usar o tema customizado
            home_name='Home',           # Renomeia o label do "home"
            sticky_nav=True,            # Navbar fixa
            sticky_mode='pinned',       # Modo Pinned
            hide_streamlit_markers=True # Esconde o menu hamburger e outros marcadores
        )

        # 'selected' agora é uma string, por exemplo "Home", "Formulário", etc.
        if selected == "Home":
            home.run()
        elif selected == "Formulário":
            preenchimento.run()
        elif selected == "Sobre":
            sobre.run()
        elif selected == "Veículos":
            veiculos.run()
        elif selected == "Logout":
            st.session_state.user = None
            st.rerun()

    else:
        # Área de Login e opção de registro
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_login"):
            if login_user(email, senha):
                user_info = get_user_info(email)
                st.session_state.user = user_info
                st.rerun()
            else:
                st.error("Credenciais inválidas!")
        
        st.markdown("---")
        st.markdown("**Não possui uma conta? Cadastre-se abaixo:**")
        register.run()

if __name__ == "__main__":
    main()
