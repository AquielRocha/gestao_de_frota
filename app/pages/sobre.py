import streamlit as st
import components.header as header


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
    header.render_header()

    
    
    st.title("s")
    st.markdown("""
  
        este é um sistema de gestão de frota de veículos
                
    """)
    
    st.image("https://img.freepik.com/free-vector/about-us-concept-illustration_114360-669.jpg", use_column_width=True)

if __name__ == "__main__":
    main()
