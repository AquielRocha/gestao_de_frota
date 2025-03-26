import streamlit as st


hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# Esconde o menu padrão do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def main():

    
    
    st.title("Bem-vindo ao Sistema de Gestão de Frota")
    st.markdown("""
    Este é o sistema para gerenciar a frota de veículos do ICMBIO.
    Aqui você pode:
    - Visualizar informações sobre os veículos.
    - Gerenciar manutenções e abastecimentos.
    - Gerar relatórios detalhados.
    """)
    
    st.image("https://image.freepik.com/free-vector/flat-people-working-car-repair-shop_74855-6268.jpg", use_column_width=True)

if __name__ == "__main__":
    main()
