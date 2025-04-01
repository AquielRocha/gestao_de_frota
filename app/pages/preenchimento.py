import streamlit as st
import pandas as pd
import re
from datetime import datetime
import sqlite3

# Import dos seus serviços (exemplo)
from app.services.auth import check_user_logged_in
from app.services.frota_service import get_veiculos_by_setor

def run():
    # 1) Verifica se o usuário está logado
    check_user_logged_in() 
    usuario = st.session_state.user
    centro_custo = usuario.get("setor_id")  # Pegando do campo correto

    centro_custo_display = re.sub(
        r"NOME NÃO ENCONTRADO ANTIGO NOME \((.+)\)", 
        r"\1", 
        centro_custo
    )

    # 2) Recupera o setor do usuário logado
    setor = st.session_state.user["setor_id"]
    st.markdown(f"## Equipamentos da Unidade {centro_custo_display}")
    
    # 3) Busca os veículos da tabela 'frota' para o setor logado
    rows, columns = get_veiculos_by_setor(setor)
    
    if rows:
        # Converte o resultado em DataFrame e renomeia as colunas para exibição correta
        df_frota = pd.DataFrame(rows, columns=columns)
        df_frota.rename(columns={
            "identificacao": "Identificação",
            "codigo_renavam": "Código Renavam",
            "numero_chassi": "Número do Chassi",
            "numero_patrimonio": "Número de Patrimônio",
            "fabricante": "Fabricante",
            "modelo": "Modelo",
            "ano_fabricacao": "Ano de Fabricação",
            "ano_modelo": "Ano do Modelo",
            "tipo_combustivel": "Combustível",
            "status": "Status",
            "cor": "Cor",
            "obs": "Observações"
        }, inplace=True)
        
        st.dataframe(df_frota)

        st.markdown("---")
        st.markdown("#### Selecione um equipamento do ano anterior para editar ou preencha os campos abaixo")
        st.markdown("**Observação:** Na tabela acima, os itens que aparecem na lista suspensa correspondem à coluna **Identificação**.")

        # Exemplo: usar a coluna 'Identificação' no selectbox
        if "Identificação" in df_frota.columns:
            lista_identificacoes = df_frota["Identificação"].dropna().unique().tolist()
            escolha_identificacao = st.selectbox(
                "Equipamento do ano anterior",
                options=[""] + lista_identificacoes
            )
        else:
            st.info("A coluna 'Identificação' não existe na frota. Selecione manualmente os campos abaixo.")
            escolha_identificacao = ""
        
        # 4) Lê a tabela de dimensões para criar selects (ex.: tipo_bem, subtipo_bem etc.)
        try:
            conn = sqlite3.connect("app/database/veiculos.db")
            df_dim = pd.read_sql_query("SELECT * FROM dimensao_frota_2024", conn)
        except Exception as e:
            st.warning(f"Não foi possível ler 'dimensao_frota_2024': {e}")
            df_dim = pd.DataFrame()
        finally:
            conn.close()

        # Cria as listas de opções (caso existam colunas)
        tipos_bem_list = df_dim["tipo_bem"].dropna().unique().tolist() if "tipo_bem" in df_dim.columns else []
        subtipos_bem_list = df_dim["subtipo_bem"].dropna().unique().tolist() if "subtipo_bem" in df_dim.columns else []
        proprietarios_list = df_dim["proprietario"].dropna().unique().tolist() if "proprietario" in df_dim.columns else []
        combustiveis_list = df_dim["combustivel"].dropna().unique().tolist() if "combustivel" in df_dim.columns else []
        status_list = df_dim["status"].dropna().unique().tolist() if "status" in df_dim.columns else []

        # Garantir "Outro" em proprietários
        if "Outro" not in proprietarios_list:
            proprietarios_list.append("Outro")

        # Inicializa variáveis que vão preencher o formulário
        tipo_bem_sel = ""
        subtipo_bem_sel = ""
        proprietario_sel = ""
        placa_sel = ""
        renavam_sel = ""
        chassi_sel = ""
        num_patrimonio_sel = ""
        fabricante_sel = ""
        modelo_sel = ""
        ano_fab_sel = ""
        ano_mod_sel = ""
        combustivel_sel = ""
        status_sel = ""
        cor_sel = ""
        observacoes_sel = ""

        # Se o usuário selecionar algum registro de frota, preenche automaticamente as variáveis
        if escolha_identificacao:
            row = df_frota[df_frota["Identificação"] == escolha_identificacao].iloc[0]
            placa_sel          = str(row["Identificação"] or "")
            renavam_sel        = str(row["Código Renavam"] or "") if "Código Renavam" in row else ""
            chassi_sel         = str(row["Número do Chassi"] or "") if "Número do Chassi" in row else ""
            num_patrimonio_sel = str(row["Número de Patrimônio"] or "") if "Número de Patrimônio" in row else ""
            fabricante_sel     = str(row["Fabricante"] or "") if "Fabricante" in row else ""
            modelo_sel         = str(row["Modelo"] or "") if "Modelo" in row else ""
            ano_fab_sel        = str(row["Ano de Fabricação"] or "") if "Ano de Fabricação" in row else ""
            ano_mod_sel        = str(row["Ano do Modelo"] or "") if "Ano do Modelo" in row else ""
            combustivel_sel    = str(row["Combustível"] or "") if "Combustível" in row else ""
            status_sel         = str(row["Status"] or "") if "Status" in row else ""
            cor_sel            = str(row["Cor"] or "") if "Cor" in row else ""
            observacoes_sel    = str(row["Observações"] or "") if "Observações" in row else ""
            proprietario_sel   = str(row["Proprietário"] or "") if "Proprietário" in row else ""

        # Sessão temporária para armazenar itens
        if "frota_temp" not in st.session_state:
            st.session_state["frota_temp"] = []

        # Indicador de qual item está sendo editado
        if "edit_index" not in st.session_state:
            st.session_state["edit_index"] = -1

        st.markdown("---")
        st.markdown("#### Formulário de Adição")

        st.write("Marque se o item possui estes campos (caso seja veículo, equipamento etc.)")
        tem_renavam = st.checkbox("Este item tem Renavam?", value=True)
        tem_chassi = st.checkbox("Este item tem Chassi?", value=True)
        tem_placa  = st.checkbox("Este item tem Placa?", value=True)

        # Patrimônio obrigatório ou justificativa
        st.write("**Número de Patrimônio** é obrigatório. Se não tiver, justifique.")
        sem_patrimonio = st.checkbox("Não tenho Nº de patrimônio?")
        if not sem_patrimonio:
            patrimonio_field = st.text_input("Número de Patrimônio (obrigatório)", max_chars=20, value=num_patrimonio_sel)
            justificativa_field = ""
        else:
            patrimonio_field = ""
            justificativa_field = st.text_input("Justificativa para ausência de Nº de Patrimônio", max_chars=50)

        with st.form("form_frota_2025", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                tipo_bem = st.selectbox("Tipo do Bem", [""] + tipos_bem_list, index=0)
                subtipo_bem = st.selectbox("Subtipo do Bem", [""] + subtipos_bem_list, index=0)

                proprietario_opt = st.selectbox("Proprietário", [""] + proprietarios_list, index=0)
                if proprietario_opt == "Outro":
                    outro_proprietario = st.text_input("Informe o Proprietário", value=proprietario_sel)
                    proprietario_final = outro_proprietario.strip() if outro_proprietario else None
                else:
                    proprietario_final = proprietario_opt.strip() if proprietario_opt else (proprietario_sel or None)

                placa = st.text_input("Placa", max_chars=8, value=placa_sel)
                if tem_renavam:
                    renavam = st.text_input("Renavam", max_chars=11, value=renavam_sel)
                else:
                    renavam = ""
            with col2:
                if tem_chassi:
                    chassi = st.text_input("Número do Chassi", max_chars=17, value=chassi_sel)
                else:
                    chassi = ""
                
                marca = st.text_input("Marca/Fabricante", value=fabricante_sel)
                modelo = st.text_input("Modelo", max_chars=30, value=modelo_sel)
                ano_fab = st.text_input("Ano de Fabricação", max_chars=4, value=ano_fab_sel)
                ano_mod = st.text_input("Ano do Modelo", max_chars=4, value=ano_mod_sel)
                combustivel = (
                    st.selectbox("Combustível", [""] + combustiveis_list, index=0)
                    if combustiveis_list else st.text_input("Combustível", value=combustivel_sel)
                )
                status = (
                    st.selectbox("Status", [""] + status_list, index=0)
                    if status_list else st.text_input("Status", value=status_sel)
                )

            cor = st.text_input("Cor", max_chars=20, value=cor_sel)
            observacoes = st.text_area("Observações", value=observacoes_sel)
            adicionar = st.form_submit_button("Adicionar Item à Lista")

        if adicionar:
            placa_up = placa.strip().upper()
            chassi_up = chassi.strip().upper()
            renavam_up = renavam.strip()

            has_error = False

            if placa_up:
                if not re.match(r"^[A-Z0-9]{7,8}$", placa_up):
                    st.error("Placa inválida! Exemplo: ABC1234.")
                    has_error = True

            if tem_renavam and renavam_up:
                if not re.match(r"^[0-9]{9,11}$", renavam_up):
                    st.error("Renavam inválido! Deve ter 9 ou 11 dígitos.")
                    has_error = True

            if tem_chassi and chassi_up:
                if not re.match(r"^[A-Z0-9]{17}$", chassi_up):
                    st.error("Chassi inválido! Ex: 9BWZZZ377VT004251 (17).")
                    has_error = True

            if ano_fab:
                if not re.match(r"^\d{4}$", ano_fab):
                    st.error("Ano de Fabricação inválido! Ex: 2020.")
                    has_error = True

            if ano_mod:
                if not re.match(r"^\d{4}$", ano_mod):
                    st.error("Ano do Modelo inválido! Ex: 2021.")
                    has_error = True

            patrimonio_final = None
            if not sem_patrimonio:
                if not patrimonio_field.strip():
                    st.error("Número de Patrimônio é obrigatório (ou justifique a ausência).")
                    has_error = True
                else:
                    patrimonio_final = patrimonio_field.strip()
            else:
                if not justificativa_field.strip():
                    st.error("Justificativa para ausência de Nº de Patrimônio é obrigatória.")
                    has_error = True
                else:
                    patrimonio_final = f"JUST: {justificativa_field.strip()}"

            if not has_error:
                novo_item = {
                    "tipo_bem": tipo_bem.strip() or None,
                    "subtipo_bem": subtipo_bem.strip() or None,
                    "proprietario": proprietario_final,
                    "placa": placa_up,
                    "renavam": renavam_up if tem_renavam else None,
                    "numero_chassi": chassi_up if tem_chassi else None,
                    "numero_patrimonio": patrimonio_final,
                    "marca": marca.strip() or None,
                    "modelo": modelo.strip() or None,
                    "ano_fabricacao": ano_fab.strip() or None,
                    "ano_modelo": ano_mod.strip() or None,
                    "combustivel": combustivel.strip() or None,
                    "status": status.strip() or None,
                    "cor": cor.strip() or None,
                    "observacao": observacoes.strip() or None,
                }
                st.session_state["frota_temp"].append(novo_item)
                st.success("Item adicionado com sucesso!")

        # Se estivermos editando algum item, exibimos o formulário de edição
        if st.session_state["edit_index"] >= 0:
            idx = st.session_state["edit_index"]
            if idx < 0 or idx >= len(st.session_state["frota_temp"]):
                st.session_state["edit_index"] = -1
                st.warning("O item que você estava editando não existe mais.")
            else:
                item_edit = st.session_state["frota_temp"][idx]
                patrimonio_val_atual = item_edit["numero_patrimonio"] or ""
                is_justificativa = patrimonio_val_atual.startswith("JUST:")

                with st.form("form_editar_frota", clear_on_submit=False):
                    tem_renavam_e = (item_edit["renavam"] is not None)
                    tem_chassi_e = (item_edit["numero_chassi"] is not None)

                    st.write("**Número de Patrimônio** é obrigatório. Se não tiver, justifique.")
                    sem_patrimonio_e = st.checkbox("Não tenho Nº de patrimônio? (edição)", value=is_justificativa)

                    if not sem_patrimonio_e:
                        patrimonio_edit = st.text_input("Número de Patrimônio (obrigatório)", max_chars=20,
                                                        value=("" if is_justificativa else patrimonio_val_atual))
                        justificativa_edit = ""
                    else:
                        patrimonio_edit = ""
                        justificativa_atual = patrimonio_val_atual.replace("JUST:", "").strip() if is_justificativa else ""
                        justificativa_edit = st.text_input("Justificativa para ausência de Nº de Patrimônio (edição)",
                                                           max_chars=50,
                                                           value=justificativa_atual)

                    col1e, col2e, col3e = st.columns(3)
                    with col1e:
                        tipo_bem_e = st.selectbox("Tipo do Bem", [""] + tipos_bem_list, index=0) if tipos_bem_list else st.text_input("Tipo do Bem", value=item_edit["tipo_bem"] or "")
                        subtipo_bem_e = st.selectbox("Subtipo do Bem", [""] + subtipos_bem_list, index=0) if subtipos_bem_list else st.text_input("Subtipo do Bem", value=item_edit["subtipo_bem"] or "")

                        proprietario_opt_e = st.selectbox("Proprietário", [""] + proprietarios_list, index=0)
                        if proprietario_opt_e == "Outro":
                            outro_proprietario_e = st.text_input("Informe o Proprietário (edição)", value=item_edit["proprietario"] or "")
                            proprietario_final_e = outro_proprietario_e.strip() if outro_proprietario_e else None
                        else:
                            proprietario_final_e = proprietario_opt_e.strip() if proprietario_opt_e else (item_edit["proprietario"] or None)

                        placa_e = st.text_input("Placa", max_chars=8, value=item_edit["placa"] or "")
                        tem_renavam_e = st.checkbox("Este item tem Renavam? (edição)", value=tem_renavam_e)
                        if tem_renavam_e:
                            renavam_e = st.text_input("Renavam", max_chars=11, value=item_edit["renavam"] or "")
                        else:
                            renavam_e = ""
                    with col2e:
                        tem_chassi_e = st.checkbox("Este item tem Chassi? (edição)", value=tem_chassi_e)
                        if tem_chassi_e:
                            chassi_e = st.text_input("Número do Chassi", max_chars=17, value=item_edit["numero_chassi"] or "")
                        else:
                            chassi_e = ""
                    with col3e:
                        tem_placa_e = st.checkbox("Este item tem Placa? (edição)", value=False)
                        if tem_placa_e:
                            placa_e = st.text_input("Número da Placa", max_chars=17, value=item_edit["placa"] or "")
                        else:
                            placa_e = ""
                        marca_e = st.text_input("Marca/Fabricante", value=item_edit["marca"] or "")
                        modelo_e = st.text_input("Modelo", max_chars=30, value=item_edit["modelo"] or "")
                        ano_fab_e = st.text_input("Ano de Fabricação", max_chars=4, value=item_edit["ano_fabricacao"] or "")
                        ano_mod_e = st.text_input("Ano do Modelo", max_chars=4, value=item_edit["ano_modelo"] or "")
                        combustivel_e = st.selectbox("Combustível", [""] + combustiveis_list, index=0) if combustiveis_list else st.text_input("Combustível", value=item_edit["combustivel"] or "")
                        status_e = st.selectbox("Status", [""] + status_list, index=0) if status_list else st.text_input("Status", value=item_edit["status"] or "")

                    cor_e = st.text_input("Cor", max_chars=20, value=item_edit["cor"] or "")
                    obs_e = st.text_area("Observações", value=item_edit["observacao"] or "")

                    editar_ok = st.form_submit_button("Salvar Edição")
                    cancelar_edicao = st.form_submit_button("Cancelar")

                if cancelar_edicao:
                    st.session_state["edit_index"] = -1
                    st.info("Edição cancelada.")
                if editar_ok:
                    has_error_edit = False

                    placa_up = placa_e.strip().upper()
                    if placa_up:
                        if not re.match(r"^[A-Z0-9]{7,8}$", placa_up):
                            st.error("Placa inválida! Exemplo: ABC1234.")
                            has_error_edit = True

                    renavam_up = renavam_e.strip()
                    if tem_renavam_e and renavam_up:
                        if not re.match(r"^[0-9]{11}$", renavam_up):
                            st.error("Renavam inválido! Deve ter 11 dígitos.")
                            has_error_edit = True

                    chassi_up = chassi_e.strip().upper()
                    if tem_chassi_e and chassi_up:
                        if not re.match(r"^[A-Z0-9]{17}$", chassi_up):
                            st.error("Chassi inválido! Deve ter 17 caracteres alfanuméricos.")
                            has_error_edit = True

                    if ano_fab_e:
                        if not re.match(r"^\d{4}$", ano_fab_e):
                            st.error("Ano de Fabricação inválido! Ex: 2020.")
                            has_error_edit = True

                    if ano_mod_e:
                        if not re.match(r"^\d{4}$", ano_mod_e):
                            st.error("Ano do Modelo inválido! Ex: 2021.")
                            has_error_edit = True

                    patrimonio_final_e = None
                    if not sem_patrimonio_e:
                        if not patrimonio_edit.strip():
                            st.error("Número de Patrimônio é obrigatório (ou justifique a ausência).")
                            has_error_edit = True
                        else:
                            patrimonio_final_e = patrimonio_edit.strip()
                    else:
                        if not justificativa_edit.strip():
                            st.error("Justificativa para ausência de Nº de Patrimônio é obrigatória.")
                            has_error_edit = True
                        else:
                            patrimonio_final_e = f"JUST: {justificativa_edit.strip()}"

                    if not has_error_edit:
                        st.session_state["frota_temp"][idx] = {
                            "tipo_bem": tipo_bem_e.strip() or None,
                            "subtipo_bem": subtipo_bem_e.strip() or None,
                            "proprietario": proprietario_final_e,
                            "placa": placa_up,
                            "renavam": renavam_up if tem_renavam_e else None,
                            "numero_chassi": chassi_up if tem_chassi_e else None,
                            "numero_patrimonio": patrimonio_final_e,
                            "marca": marca_e.strip() or None,
                            "modelo": modelo_e.strip() or None,
                            "ano_fabricacao": ano_fab_e.strip() or None,
                            "ano_modelo": ano_mod_e.strip() or None,
                            "combustivel": combustivel_e.strip() or None,
                            "status": status_e.strip() or None,
                            "cor": cor_e.strip() or None,
                            "observacao": obs_e.strip() or None,
                        }
                        st.session_state["edit_index"] = -1
                        st.success("Edição salva com sucesso!")

        # Listagem dos itens adicionados (temporários) – versão simplificada e mais bonita
        st.markdown("---")
        st.markdown("#### Itens Adicionados (salve antes de sair)")
        if len(st.session_state["frota_temp"]) == 0:
            st.info("Nenhum item adicionado ainda.")
        else:
            for i, item in enumerate(st.session_state["frota_temp"], 1):
                with st.expander(f"Item #{i}: {item.get('tipo_bem') or 'Sem Tipo'}", expanded=False):
                    st.write(f"**Subtipo:** {item.get('subtipo_bem') or ''}")
                    st.write(f"**Proprietário:** {item.get('proprietario') or ''}")
                    st.write(f"**Placa:** {item.get('placa') or ''}")
                    st.write(f"**Renavam:** {item.get('renavam') or ''}")
                    st.write(f"**Chassi:** {item.get('numero_chassi') or ''}")
                    st.write(f"**Número de Patrimônio:** {item.get('numero_patrimonio') or ''}")
                    st.write(f"**Marca:** {item.get('marca') or ''}")
                    st.write(f"**Modelo:** {item.get('modelo') or ''}")
                    st.write(f"**Ano de Fabricação:** {item.get('ano_fabricacao') or ''}")
                    st.write(f"**Ano do Modelo:** {item.get('ano_modelo') or ''}")
                    st.write(f"**Combustível:** {item.get('combustivel') or ''}")
                    st.write(f"**Status:** {item.get('status') or ''}")
                    st.write(f"**Cor:** {item.get('cor') or ''}")
                    st.write(f"**Observações:** {item.get('observacao') or ''}")
                    
                    # Botões de edição/exclusão
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button(f"Editar #{i}", key=f"btn_edit_{i}"):
                            st.session_state["edit_index"] = i - 1
                    with col_del:
                        if st.button(f"Excluir #{i}", key=f"btn_del_{i}"):
                            st.session_state["frota_temp"].pop(i - 1)
                            st.success(f"Item #{i} removido.")
                            st.rerun()

                    # Linha divisória entre itens
                    st.write("---")

        # Botão para salvar todos os itens no banco (frota_2025)
        if len(st.session_state["frota_temp"]) > 0:
            st.markdown("---")
            if st.button("Salvar todos no Banco de Dados (frota_2025)"):
                try:
                    conn = sqlite3.connect("app/database/veiculos.db")
                    cursor = conn.cursor()
                    insert_query = """
                        INSERT INTO frota_2025 (
                            usuario_id,
                            setor_id,
                            data_preenchimento,
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
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    usuario_id = st.session_state.user["id"] if "user" in st.session_state else 1
                    setor_id = st.session_state.user["setor_id"] if "user" in st.session_state else 1

                    for item in st.session_state["frota_temp"]:
                        data_preenchimento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        dados = (
                            usuario_id,
                            setor_id,
                            data_preenchimento,
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
                        )
                        cursor.execute(insert_query, dados)

                    conn.commit()
                    conn.close()

                    st.session_state["frota_temp"].clear()
                    st.success("Todos os itens foram salvos na tabela frota_2025 com sucesso!")

                except Exception as e:
                    st.error(f"Erro ao inserir dados: {e}")

    else:
        st.info("Nenhum veículo encontrado para este setor.")
