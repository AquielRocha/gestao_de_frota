import streamlit as st

# Esconde a barra lateral do Streamlit
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

    st.title("Formulário de Preenchimento de Frota")

    # Campos do formulário
    st.subheader("Informações do Veículo")
    tipo_veiculo = st.selectbox("Tipo de Veículo", ["Carro", "Moto", "Caminhão", "Ônibus", "Outro"])
    marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Toyota", "Honda", "Volkswagen", "Outro"])
    modelo = st.text_input("Modelo")
    ano = st.number_input("Ano de Fabricação", min_value=1900, max_value=2023, step=1)
    placa = st.text_input("Placa do Veículo")

    st.subheader("Informações do Motorista")
    nome_motorista = st.text_input("Nome do Motorista")
    cnh = st.text_input("Número da CNH")
    validade_cnh = st.date_input("Validade da CNH")

    st.subheader("Informações Adicionais")
    quilometragem = st.number_input("Quilometragem Atual", min_value=0, step=1)
    combustivel = st.selectbox("Tipo de Combustível", ["Gasolina", "Álcool", "Diesel", "GNV", "Elétrico", "Outro"])
    observacoes = st.text_area("Observações")

    # Botão de envio
    if st.button("Enviar"):
        st.success("Formulário enviado com sucesso!")
        # Aqui você pode adicionar lógica para salvar os dados em um banco de dados ou arquivo

if __name__ == "__main__":
    main()