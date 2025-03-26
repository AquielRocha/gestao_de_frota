# components/header.py
import streamlit as st


hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
def render_header():
    st.markdown(
        """
        <style>
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #4e54c8, #8f94fb);
            padding: 15px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            position: fixed;
            top: 10px;
            left: 10px;
            right: 10px;
            z-index: 1000;
        }
        .navbar a {
            text-decoration: none;
            color: #ffffff;
            font-size: 18px;
            font-weight: 600;
            margin: 0 15px;
            transition: color 0.3s ease, transform 0.3s ease;
        }
        .navbar a:hover {
            color: #d1d1ff;
            transform: translateY(-3px);
        }
        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
        }
        body {
            margin-top: 80px; /* Espaço para o header fixo */
        }
        </style>
        <div class="navbar">
            <div class="logo">Gestão de Frota</div>
            <div class="menu">
                <a href="/home" target="_self">Home</a>
                <a href="/preenchimento" target="_self">Preenchimento</a>
                <a href="/sobre" target="_self">Sobre</a>
                <a href="/?page=contact" target="_self">Contato</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Para testes locais
if __name__ == "__main__":
    st.set_page_config(page_title="Exemplo de Navbar", layout="wide")
    render_header()
    page = st.query_params().get("page", ["home"])[0]
    if page == "home":
        st.title("Bem-vindo à Home")
    elif page == "about":
        st.title("Sobre Nós")
    elif page == "Preenchimento":
        st.title("Formulário de Preenchimento de Frota")
    elif page == "contact":
        st.title("Entre em Contato")
    else:
        st.title("Página Não Encontrada")
