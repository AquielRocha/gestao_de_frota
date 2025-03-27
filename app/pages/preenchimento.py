import streamlit as st
from app.services.frota_service import inserir_veiculo

def show():
    st.subheader("Cadastro de Veículo - Frota 2025")
    with st.form("form_veiculo"):
        tipo_bem = st.selectbox("Tipo do Bem", ["Veículo", "Embarcação", "Equipamento"])
        subtipo_bem = st.text_input("Subtipo do Bem")
        placa = st.text_input("Placa")
        numero_chassi = st.text_input("Chassi ou Nº de Série")
        renavam = st.text_input("Renavam")
        numero_patrimonio = st.text_input("Nº Patrimônio")
        proprietario = st.text_input("Proprietário")
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        ano_fabricacao = st.number_input("Ano Fabricação", min_value=1900, max_value=2100)
        ano_modelo = st.number_input("Ano Modelo", min_value=1900, max_value=2100)
        cor = st.text_input("Cor")
        combustivel = st.text_input("Combustível")
        status = st.selectbox("Status", ["Ativo", "Ocioso", "Antieconômico", "Irrecuperável"])
        observacao = st.text_area("Observação")
        adicionar_mais = st.checkbox("Deseja adicionar mais um item?")

        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            inserir_veiculo(
                1, 1, tipo_bem, subtipo_bem, placa, numero_chassi, renavam,
                numero_patrimonio, proprietario, marca, modelo,
                ano_fabricacao, ano_modelo, cor, combustivel,
                status, observacao, int(adicionar_mais)
            )
            st.success("Veículo cadastrado com sucesso!")
