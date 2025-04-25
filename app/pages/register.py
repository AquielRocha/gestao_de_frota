import streamlit as st
from app.services.auth import create_user, get_setor_options

# ------------------------------------------------------------------ #
def run():
    st.markdown("<div class='login-title'>Crie sua Conta</div>",
                unsafe_allow_html=True)

    with st.form("register_form"):
        nome  = st.text_input("Nome completo")
        cpf   = st.text_input("CPF (só números)", max_chars=11)
        email = st.text_input("Email")
        pwd   = st.text_input("Senha", type="password")

        # ----- select de setor -----
        setores = get_setor_options()
        if not setores:
            st.warning("Nenhum setor cadastrado — chama o admin.")
            setor_codigo = None
        else:
            label = [f"{s['sigla']} - {s['nome']}" for s in setores]
            escolha = st.selectbox("Setor / Centro de Custo", label)
            setor_codigo = next(
                s["codigo"] for s in setores
                if f"{s['sigla']} - {s['nome']}" == escolha
            )

        submit = st.form_submit_button("Cadastrar")
    # fora do with!

    if submit:
        if not setor_codigo:
            st.error("Escolhe um setor válido, pô!")
        else:
            ok = create_user(nome, cpf, pwd, email, setor_codigo)
            if ok:
                st.success("Cadastro feito! Agora faz login.")
            else:
                st.error("CPF ou email já existe, maluco.")

    if st.button("Voltar ao Login"):
        st.session_state.show_registration = False
        st.rerun()
