import streamlit as st
import sqlite3
import pandas as pd
import re  # Usado para validações por expressão regular
from app.services.auth import check_user_logged_in


def run():
    check_user_logged_in()

    # --- Pequena customização CSS para dar fundo claro e "cards" ---
    st.markdown("""
        <style>
            /* Define um fundo suave para o app */
            .stApp {
                background-color: #F9F9F9;
            }
            /* Classe card para exibir itens adicionados */
            .card {
                background-color: #FFFFFF;
                padding: 1rem;
                margin-bottom: 1rem;
                border-radius: 0.5rem;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            }
            /* Títulos maiores e em negrito */
            .title-text {
                font-size: 1.3rem;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='title-text'>Gestão de Frota 2025</h2>", unsafe_allow_html=True)
    st.write("Preencha as informações .")

    # --- Conexão e leitura dos dados existentes ---
    conn = sqlite3.connect("app/database/veiculos.db")
    cursor = conn.cursor()
    df_dim = pd.read_sql_query("SELECT * FROM dimensao_frota_2024", conn)

    # Listas de opções (ajuste se as colunas tiverem nomes diferentes)
    tipos_bem = df_dim["tipo_bem"].dropna().unique().tolist() if "tipo_bem" in df_dim.columns else []
    subtipos_bem = df_dim["subtipo_bem"].dropna().unique().tolist() if "subtipo_bem" in df_dim.columns else []
    proprietarios = df_dim["proprietario"].dropna().unique().tolist() if "proprietario" in df_dim.columns else []
    fabricantes = df_dim["marca"].dropna().unique().tolist() if "marca" in df_dim.columns else []
    modelos_bd = df_dim["modelo"].dropna().unique().tolist() if "modelo" in df_dim.columns else []
    combustiveis = df_dim["combustivel"].dropna().unique().tolist() if "combustivel" in df_dim.columns else []
    status_list = df_dim["status"].dropna().unique().tolist() if "status" in df_dim.columns else []

    # Garante opção "Outro" no proprietário
    if "Outro" not in proprietarios:
        proprietarios.append("Outro")

    # Sessão temporária para armazenar itens
    if "frota_temp" not in st.session_state:
        st.session_state["frota_temp"] = []

    # Indicador de qual item está sendo editado (-1 se nenhum)
    if "edit_index" not in st.session_state:
        st.session_state["edit_index"] = -1

    # ----------------------------------------------------------------
    # Formulário de ADIÇÃO
    # ----------------------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p class='title-text'>Adicionar Novo Item</p>", unsafe_allow_html=True)

    with st.form("form_frota_2024", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo_bem_sel = st.selectbox("Tipo do Bem", [""] + tipos_bem)
            subtipo_bem_sel = st.selectbox("Subtipo do Bem", [""] + subtipos_bem)
            proprietario_sel = st.selectbox("Proprietário", [""] + proprietarios)
            outro_proprietario = st.text_input("Informe o Proprietário") if proprietario_sel == "Outro" else ""

            placa_sel = st.text_input("Placa", max_chars=8)
            renavam_sel = st.text_input("Renavam", max_chars=11)
            num_patrimonio_sel = st.text_input("Número de Patrimônio (se existir)", max_chars=20)

        with col2:
            chassi_sel = st.text_input("Número do Chassi", max_chars=17)
            fabricante_sel = st.selectbox("Marca/Fabricante", [""] + fabricantes)
            modelo_sel = st.text_input("Modelo", max_chars=30)
            ano_fab_sel = st.text_input("Ano Fabricação", max_chars=4)
            ano_mod_sel = st.text_input("Ano Modelo", max_chars=4)
            combustivel_sel = st.selectbox("Combustível", [""] + combustiveis)
            status_sel = st.selectbox("Status", [""] + status_list)

        cor_sel = st.text_input("Cor", max_chars=20)
        observacoes_sel = st.text_area("Observações")

        adicionar = st.form_submit_button("Adicionar")

    # --- Validação do formulário de ADIÇÃO ---
    if adicionar:
        placa_up = placa_sel.strip().upper()
        chassi_up = chassi_sel.strip().upper()
        renavam_up = renavam_sel.strip()

        # Se "Outro" foi escolhido, usar o valor digitado
        proprietario_final = outro_proprietario.strip() if proprietario_sel == "Outro" else proprietario_sel

        has_error = False

        # Valida Placa
        if placa_up:
            if not re.match(r"^[A-Z0-9]{7,8}$", placa_up):
                st.error("Placa inválida! Exemplo: ABC1234. Limpamos o campo para você corrigir.")
                placa_up = ""
                st.session_state["form_frota_2024-Placa"] = ""
                has_error = True

        # Valida Renavam (11 dígitos)
        if renavam_up:
            if not re.match(r"^[0-9]{11}$", renavam_up):
                st.error("Renavam inválido! Exemplo: 12345678901 (11 dígitos). Limpamos o campo para corrigir.")
                renavam_up = ""
                st.session_state["form_frota_2024-Renavam"] = ""
                has_error = True

        # Valida Chassi (17 caracteres alfanuméricos)
        if chassi_up:
            if not re.match(r"^[A-Z0-9]{17}$", chassi_up):
                st.error("Chassi inválido! Exemplo: 9BWZZZ377VT004251 (17). Limpamos o campo para corrigir.")
                chassi_up = ""
                st.session_state["form_frota_2024-Número do Chassi"] = ""
                has_error = True

        # Valida Anos
        ano_fab_ok = ano_fab_sel.strip()
        ano_mod_ok = ano_mod_sel.strip()

        if ano_fab_ok:
            if not re.match(r"^\d{4}$", ano_fab_ok):
                st.error("Ano de Fabricação inválido! Ex: 2020. Limpamos o campo para corrigir.")
                ano_fab_ok = ""
                st.session_state["form_frota_2024-Ano Fabricação"] = ""
                has_error = True

        if ano_mod_ok:
            if not re.match(r"^\d{4}$", ano_mod_ok):
                st.error("Ano Modelo inválido! Ex: 2021. Limpamos o campo para corrigir.")
                ano_mod_ok = ""
                st.session_state["form_frota_2024-Ano Modelo"] = ""
                has_error = True

        if not has_error:
            # Se tudo OK, adiciona
            novo_item = {
                "tipo_bem": tipo_bem_sel.strip() or None,
                "subtipo_bem": subtipo_bem_sel.strip() or None,
                "proprietario": proprietario_final.strip() or None,
                "placa": placa_up,
                "renavam": renavam_up,
                "numero_chassi": chassi_up,
                "numero_patrimonio": num_patrimonio_sel.strip() or None,
                "marca": fabricante_sel.strip() or None,
                "modelo": modelo_sel.strip() or None,
                "ano_fabricacao": ano_fab_ok or None,
                "ano_modelo": ano_mod_ok or None,
                "combustivel": combustivel_sel.strip() or None,
                "status": status_sel.strip() or None,
                "cor": cor_sel.strip() or None,
                "observacao": observacoes_sel.strip() or None,
            }
            st.session_state["frota_temp"].append(novo_item)
            st.success("Item adicionado com sucesso!")

    # ----------------------------------------------------------------
    # Se estivermos editando algum item, exibir FORMULÁRIO DE EDIÇÃO
    # ----------------------------------------------------------------
    if st.session_state["edit_index"] >= 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<p class='title-text'>Editar Item</p>", unsafe_allow_html=True)
        idx = st.session_state["edit_index"]
        item_edit = st.session_state["frota_temp"][idx]

        with st.form("form_editar_frota", clear_on_submit=False):
            col1e, col2e = st.columns(2)
            with col1e:
                tipo_bem_e = st.text_input("Tipo do Bem", value=item_edit["tipo_bem"] or "")
                subtipo_bem_e = st.text_input("Subtipo do Bem", value=item_edit["subtipo_bem"] or "")
                proprietario_e = st.text_input("Proprietário", value=item_edit["proprietario"] or "")
                placa_e = st.text_input("Placa", max_chars=8, value=item_edit["placa"] or "")
                renavam_e = st.text_input("Renavam", max_chars=11, value=item_edit["renavam"] or "")
                num_patrimonio_e = st.text_input("Número de Patrimônio", max_chars=20, value=item_edit["numero_patrimonio"] or "")

            with col2e:
                chassi_e = st.text_input("Número do Chassi", max_chars=17, value=item_edit["numero_chassi"] or "")
                marca_e = st.text_input("Marca/Fabricante", value=item_edit["marca"] or "")
                modelo_e = st.text_input("Modelo", max_chars=30, value=item_edit["modelo"] or "")
                ano_fab_e = st.text_input("Ano Fabricação", max_chars=4, value=item_edit["ano_fabricacao"] or "")
                ano_mod_e = st.text_input("Ano Modelo", max_chars=4, value=item_edit["ano_modelo"] or "")
                combustivel_e = st.text_input("Combustível", value=item_edit["combustivel"] or "")
                status_e = st.text_input("Status", value=item_edit["status"] or "")

            cor_e = st.text_input("Cor", max_chars=20, value=item_edit["cor"] or "")
            obs_e = st.text_area("Observações", value=item_edit["observacao"] or "")

            editar_ok = st.form_submit_button("Salvar Edição")
            cancelar_edicao = st.form_submit_button("Cancelar")

        # -- CANCELAR EDIÇÃO --
        if cancelar_edicao:
            st.session_state["edit_index"] = -1
            st.info("Edição cancelada.")

        # -- SALVAR EDIÇÃO --
        if editar_ok:
            # Faz as mesmas validações
            placa_up = placa_e.strip().upper()
            chassi_up = chassi_e.strip().upper()
            renavam_up = renavam_e.strip()

            has_error_edit = False

            # Valida Placa
            if placa_up:
                if not re.match(r"^[A-Z0-9]{7,8}$", placa_up):
                    st.error("Placa inválida! Ex: ABC1234. Corrija por favor.")
                    has_error_edit = True
            # Valida Renavam
            if renavam_up:
                if not re.match(r"^[0-9]{11}$", renavam_up):
                    st.error("Renavam inválido! Ex: 12345678901 (11 dígitos).")
                    has_error_edit = True
            # Valida Chassi
            if chassi_up:
                if not re.match(r"^[A-Z0-9]{17}$", chassi_up):
                    st.error("Chassi inválido! Ex: 9BWZZZ377VT004251 (17).")
                    has_error_edit = True

            # Valida Anos
            ano_fab_ok = ano_fab_e.strip()
            ano_mod_ok = ano_mod_e.strip()

            if ano_fab_ok:
                if not re.match(r"^\d{4}$", ano_fab_ok):
                    st.error("Ano Fabricação inválido! Ex: 2020.")
                    has_error_edit = True

            if ano_mod_ok:
                if not re.match(r"^\d{4}$", ano_mod_ok):
                    st.error("Ano Modelo inválido! Ex: 2021.")
                    has_error_edit = True

            if not has_error_edit:
                # Se sem erros, atualiza o item
                st.session_state["frota_temp"][idx] = {
                    "tipo_bem": tipo_bem_e.strip() or None,
                    "subtipo_bem": subtipo_bem_e.strip() or None,
                    "proprietario": proprietario_e.strip() or None,
                    "placa": placa_up,
                    "renavam": renavam_up,
                    "numero_chassi": chassi_up,
                    "numero_patrimonio": num_patrimonio_e.strip() or None,
                    "marca": marca_e.strip() or None,
                    "modelo": modelo_e.strip() or None,
                    "ano_fabricacao": ano_fab_ok or None,
                    "ano_modelo": ano_mod_ok or None,
                    "combustivel": combustivel_e.strip() or None,
                    "status": status_e.strip() or None,
                    "cor": cor_e.strip() or None,
                    "observacao": obs_e.strip() or None,
                }
                st.session_state["edit_index"] = -1
                st.success("Edição salva com sucesso!")

    # ----------------------------------------------------------------
    # Listagem dos itens para EDIÇÃO/EXCLUSÃO
    # ----------------------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p class='title-text'>Itens adicionados (temporários)</p>", unsafe_allow_html=True)

    if len(st.session_state["frota_temp"]) == 0:
        st.info("Nenhum item adicionado ainda.")
    else:
        for i, item in enumerate(st.session_state["frota_temp"], 1):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**#{i} - {item.get('tipo_bem') or 'Sem Tipo'}**")
            st.write(
                f"- **Subtipo:** {item.get('subtipo_bem') or ''}\n"
                f"- **Proprietário:** {item.get('proprietario') or ''}\n"
                f"- **Placa:** {item.get('placa') or ''}\n"
                f"- **Renavam:** {item.get('renavam') or ''}\n"
                f"- **Número do Chassi:** {item.get('numero_chassi') or ''}\n"
                f"- **Número de Patrimônio:** {item.get('numero_patrimonio') or ''}\n"
                f"- **Marca:** {item.get('marca') or ''}\n"
                f"- **Modelo:** {item.get('modelo') or ''}\n"
                f"- **Ano Fabricação:** {item.get('ano_fabricacao') or ''}\n"
                f"- **Ano Modelo:** {item.get('ano_modelo') or ''}\n"
                f"- **Combustível:** {item.get('combustivel') or ''}\n"
                f"- **Status:** {item.get('status') or ''}\n"
                f"- **Cor:** {item.get('cor') or ''}\n"
                f"- **Observações:** {item.get('observacao') or ''}"
            )

            # Colunas para botões de Ação: Editar, Excluir
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button(f"Editar #{i}", key=f"btn_edit_{i}"):
                    st.session_state["edit_index"] = i - 1  # 0-based

            with ac2:
                if st.button(f"Excluir #{i}", key=f"btn_del_{i}"):
                    st.session_state["frota_temp"].pop(i - 1)
                    st.success(f"Item #{i} removido.")
                    st.rerun()  # Recarregar a tela pra atualizar a lista

            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # Botão para salvar todos no banco de dados
    # ----------------------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    if len(st.session_state["frota_temp"]) > 0:
        if st.button("Salvar todos no Banco de Dados"):
            usuario_id = 1
            setor_id = 1

            try:
                insert_query = """
                    INSERT INTO frota_2025 (
                        usuario_id,
                        setor_id,
                        tipo_bem,
                        subtipo_bem,
                        placa,
                        numero_chassi,
                        renavam,
                        numero_patrimonio,
                        proprietario,
                        marca,
                        modelo,
                        ano_fabricacao,
                        ano_modelo,
                        cor,
                        combustivel,
                        status,
                        observacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                for item in st.session_state["frota_temp"]:
                    cursor.execute(insert_query, (
                        usuario_id,
                        setor_id,
                        item.get("tipo_bem"),
                        item.get("subtipo_bem"),
                        item.get("placa"),
                        item.get("numero_chassi"),
                        item.get("renavam"),
                        item.get("numero_patrimonio"),
                        item.get("proprietario"),
                        item.get("marca"),
                        item.get("modelo"),
                        item.get("ano_fabricacao"),
                        item.get("ano_modelo"),
                        item.get("cor"),
                        item.get("combustivel"),
                        item.get("status"),
                        item.get("observacao"),
                    ))
                conn.commit()
                st.session_state["frota_temp"].clear()
                st.success("Todos os itens foram salvos no banco de dados com sucesso!")
            except Exception as e:
                st.error(f"Erro ao inserir dados: {e}")

    conn.close()
