import streamlit as st
from app.services.auth import check_user_logged_in

def run():
    check_user_logged_in()

    st.markdown("""
        <style>
        .card{background:#f0f2f6;border-radius:12px;padding:20px;margin-bottom:30px;
              box-shadow:0 4px 12px rgba(0,0,0,.1);}
        .card h2{font-size:22px;margin-bottom:10px;color:#333;}
        .card p {font-size:15px;color:#666;}
        </style>
    """, unsafe_allow_html=True)

    st.title("Guia Visual - Cadastro de Equipamentos no Sistema de Frota")

    # ── Card 1 ─────────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <h2>🧾 1. Nomenclatura Padrão de Equipamentos</h2>
      <p>Utilize os prefixos de identificação conforme o tipo de equipamento.
         O código será composto por 3 letras + 4 dígitos sequenciais.</p>
    </div>""", unsafe_allow_html=True)
    st.image("app/assets/tere.png",
             caption="Tabela de Nomenclatura - DFROT",
             use_container_width=True)

    # ── Card 2 ─────────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <h2>🖥️ 2. Preenchimento do Cadastro no Sistema</h2>
      <p>Insira os dados obrigatórios como Identificação, Número de Série,
         Proprietário e demais informações técnicas do equipamento.</p>
    </div>""", unsafe_allow_html=True)
    st.image("app/assets/tere2.png",
             caption="Tela de Cadastro - Maxifrota",
             use_container_width=True)

    # ── Card 3 ─────────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <h2>📛 3. Classificação de Frota</h2>
      <p>Os bens sem necessidade de emplacamento recebem um código composto
         por 3 letras + 4 números, de acordo com a nomenclatura definida.</p>
    </div>""", unsafe_allow_html=True)
    st.image("app/assets/tere3.png",
             caption="Exemplo de Código de Frota",
             use_container_width=True)

    st.success("Para dúvidas, entre em contato com a DFROT.")
