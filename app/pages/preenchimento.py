import streamlit as st
import pandas as pd
import re
from datetime import datetime
import sqlite3

# Import dos seus serviços (exemplo)
from app.services.auth import check_user_logged_in
from app.services.frota_service import get_veiculos_by_setor
from app.pages import home, preenchimento, sobre, veiculos, register, usuarios, exportacao

def run():
    # --------------------------------------------------
    # Estilos CSS (cores atualizadas, cabeçalho visível)
    # --------------------------------------------------
    st.markdown(
        """
        <style>
        /* Variáveis de cores */
        :root {
            --bg: #f7fafc;
            --bg-card: #ffffff;
            --primary: #2d3748;
            --primary-light: #4a5568;
            --text: #2d3748;
            --border: #e2e8f0;
            --accent: #edf2f7;
        }
        /* Botão “Salvar todos os itens” */
        div.stButton > button#save_button {
            background-color: var(--primary) !important;
            color: #fff !important;
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
        }
        /* Cartão da tabela */
        .frota-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 12px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }
        /* Scrollbar */
        .frota-card::-webkit-scrollbar {
            height: 6px; width: 6px;
        }
        .frota-card::-webkit-scrollbar-track {
            background: var(--accent);
        }
        .frota-card::-webkit-scrollbar-thumb {
            background: var(--primary-light);
            border-radius: 4px;
        }
        /* Tabela */
        .frota-table {
            width: 100%;
            min-width: 600px;
            border-collapse: collapse;
            font-size: 15px;
            color: var(--text);
        }
        .frota-table th, .frota-table td {
            padding: 8px;
            border: 1px solid var(--border);
            text-align: left;
        }
        /* Cabeçalho fixo e visível */
        .frota-table thead {
            background: var(--primary);
            color: #fff;
        }
        .frota-table thead th {
            position: sticky;
            top: 0;
            z-index: 10;
            background: var(--primary);
        }
        .frota-table tbody tr:nth-child(odd) {
            background: var(--accent);
        }
        .frota-table tbody tr:hover {
            background: var(--primary-light);
            color: #fff;
        }
        @media (max-width: 640px) {
            .frota-table th, .frota-table td {
                padding: 7px;
                font-size: 12px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------
    # Barra de busca (sem ícone)
    # ---------------------------
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <input
                type="text"
                id="searchInput"
                placeholder="Buscar itens..."
                style="width:100%; padding:8px; border:1px solid var(--border); border-radius:4px; font-size:14px;"
            >
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------
    # Autenticação e título
    # ---------------------------
    check_user_logged_in()
    usuario = st.session_state.user
    centro_custo = usuario.get("setor_id", "")
    centro_custo_display = re.sub(
        r"NOME NÃO ENCONTRADO ANTIGO NOME \\((.+)\\)",
        r"\1",
        centro_custo
    )
    setor = usuario.get("setor_id", "")
    st.markdown(f"## Equipamentos da Unidade {centro_custo_display}")

    # ---------------------------
    # Busca de dados
    # ---------------------------
    rows, columns = get_veiculos_by_setor(setor)
    if rows:
        df_frota = pd.DataFrame(rows, columns=columns)
        # Esconde colunas irrelevantes
        df_frota.drop(columns=["id", "quantidade"], inplace=True, errors="ignore")
        # Renomeia colunas
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
            "obs": "Observações",
            "proprietario": "Proprietário"
        }, inplace=True)

        # Itens já salvos
        conn = sqlite3.connect("app/database/veiculos.db")
        df_existentes = pd.read_sql_query(
            "SELECT placa FROM frota_2025 WHERE setor_id = ?",
            params=(setor,),
            con=conn
        )
        conn.close()
        if not df_existentes.empty:
            df_frota = df_frota[~df_frota["Identificação"].isin(df_existentes["placa"])]

        if df_frota.empty:
            st.info("Todos os itens desta unidade que estavam desatualizados foram atualizados!.")
            st.write("Ainda assim, você pode adicionar **novos itens** que não fazem parte da tabela frota original.")
        else:
            html = df_frota.to_html(classes="frota-table", index=False, border=0, escape=False)
            st.markdown(f'<div class="frota-card">{html}</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(
                "#### Selecione um equipamento do ano anterior para pré-preenchimento dos campos."
            )
            opcoes = df_frota["Identificação"].dropna().unique().tolist()
            escolha = st.selectbox("Equipamento do ano anterior", options=[""] + opcoes)
            # Preenche valores iniciais
            if escolha:
                sel = df_frota[df_frota["Identificação"] == escolha].iloc[0]
                placa_sel          = sel["Identificação"]
                renavam_sel        = sel["Código Renavam"]
                chassi_sel         = sel["Número do Chassi"]
                num_patrimonio_sel = sel["Número de Patrimônio"]
                fabricante_sel     = sel["Fabricante"]
                modelo_sel         = sel["Modelo"]
                ano_fab_sel        = sel["Ano de Fabricação"]
                ano_mod_sel        = sel["Ano do Modelo"]
                combustivel_sel    = sel["Combustível"]
                status_sel         = sel["Status"]
                cor_sel            = sel["Cor"]
                observacoes_sel    = sel["Observações"]
                proprietario_sel   = sel["Proprietário"]
            else:
                placa_sel = renavam_sel = chassi_sel = num_patrimonio_sel = ""
                fabricante_sel = modelo_sel = ano_fab_sel = ano_mod_sel = ""
                combustivel_sel = status_sel = cor_sel = observacoes_sel = proprietario_sel = ""
    else:
        st.info("Nenhum veículo encontrado para este setor.")
        placa_sel = renavam_sel = chassi_sel = num_patrimonio_sel = ""
        fabricante_sel = modelo_sel = ano_fab_sel = ano_mod_sel = ""
        combustivel_sel = status_sel = cor_sel = observacoes_sel = proprietario_sel = ""

    # ------------------------------------------------------------------
    # Formulário de adição de novo equipamento
    # ------------------------------------------------------------------
    # Busca dimensões para dropdowns
    try:
        conn = sqlite3.connect("app/database/veiculos.db")
        df_dim = pd.read_sql_query("SELECT * FROM dimensao_frota_2024", conn)
    except Exception as e:
        st.warning(f"Erro ao ler dimensões: {e}")
        df_dim = pd.DataFrame()
    finally:
        conn.close()

    tipos  = df_dim["tipo_bem"].dropna().unique().tolist() if "tipo_bem" in df_dim else []
    subtps = df_dim["subtipo_bem"].dropna().unique().tolist() if "subtipo_bem" in df_dim else []
    props  = df_dim["proprietario"].dropna().unique().tolist() if "proprietario" in df_dim else []
    combs  = df_dim["combustivel"].dropna().unique().tolist() if "combustivel" in df_dim else []
    stats  = df_dim["status"].dropna().unique().tolist() if "status" in df_dim else []

    if "Outro" not in props:
        props.append("Outro")

    if "frota_temp" not in st.session_state:
        st.session_state["frota_temp"] = []
    if "edit_index" not in st.session_state:
        st.session_state["edit_index"] = -1

    st.markdown("---")
    st.markdown("#### Adicionar novo equipamento")
    tem_renavam = st.checkbox("Este item tem Renavam?", value=True)
    tem_chassi = st.checkbox("Este item tem Chassi?", value=True)
    tem_placa = st.checkbox("Este item tem Placa?", value=True)

    st.markdown("""
        <div style="background-color:#fff8c4; padding:10px; border-left:5px solid #e6b800; border-radius:5px;">
        <strong>Número de Patrimônio</strong> é obrigatório. Se não tiver, justifique.
        </div>
    """, unsafe_allow_html=True)

    sem_patr = st.checkbox("Não tenho Nº de patrimônio?")
    if not sem_patr:
        patr_field = st.text_input("Número de Patrimônio (obrigatório)", value=num_patrimonio_sel)
        justif = ""
    else:
        patr_field = ""
        justif = st.text_input("Justificativa para ausência do Nº de Patrimônio")

    with st.form("form_add", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            tipo_sel   = st.selectbox("Tipo do Bem", [""]+tipos)
            subito_sel = st.selectbox("Subtipo do Bem", [""]+subtps)
            prop_sel   = st.selectbox("Proprietário", [""]+props)
            if prop_sel == "Outro":
                prop_final = st.text_input("Informe o Proprietário", value=proprietario_sel)
            else:
                prop_final = prop_sel or proprietario_sel
            if tem_placa:
                placa = st.text_input("Placa/Identificação", value=placa_sel)
            else:
                placa = ""
            if tem_renavam:
                renavam = st.text_input("Renavam", value=renavam_sel)
            else:
                renavam = ""
        with c2:
            if tem_chassi:
                chassi = st.text_input("Número do Chassi", value=chassi_sel)
            else:
                chassi = ""
            marca = st.text_input("Marca/Fabricante", value=fabricante_sel)
            modelo = st.text_input("Modelo", value=modelo_sel)
            ano_fab = st.text_input("Ano de Fabricação", value=ano_fab_sel)
            ano_mod = st.text_input("Ano do Modelo", value=ano_mod_sel)
            combust = st.selectbox("Combustível", [""]+combs) if combs else st.text_input("Combustível", value=combustivel_sel)
            status = st.selectbox("Status", [""]+stats) if stats else st.text_input("Status", value=status_sel)
            cor = st.text_input("Cor", value=cor_sel)
        obs = st.text_area("Observações", value=observacoes_sel)
        btn = st.form_submit_button("Adicionar Item à Lista")

    if btn:
        errors = False
        if tem_renavam and renavam and not re.match(r"^[0-9]{9,11}$", renavam):
            st.error("Renavam inválido! Deve ter 9 ou 11 dígitos.")
            errors = True
        if ano_fab and not re.match(r"^\d{4}$", ano_fab):
            st.error("Ano de Fabricação inválido!")
            errors = True
        if ano_mod and not re.match(r"^\d{4}$", ano_mod):
            st.error("Ano do Modelo inválido!")
            errors = True
        if not sem_patr and not patr_field.strip():
            st.error("Número de Patrimônio é obrigatório.")
            errors = True
        if sem_patr and not justif.strip():
            st.error("Justificativa obrigatória.")
            errors = True

        if not errors:
            final_patr = patr_field if not sem_patr else f"JUST: {justif}"
            item = {
              "tipo_bem": tipo_sel,
              "subtipo_bem": subito_sel,
              "proprietario": prop_final,
              "placa": placa,
              "renavam": renavam if tem_renavam else None,
              "numero_chassi": chassi if tem_chassi else None,
              "numero_patrimonio": final_patr,
              "marca": marca,
              "modelo": modelo,
              "ano_fabricacao": ano_fab,
              "ano_modelo": ano_mod,
              "combustivel": combust,
              "status": status,
              "cor": cor,
              "observacao": obs
            }
            st.session_state["frota_temp"].append(item)
            st.success("Item adicionado com sucesso!")

    # ------------------------------------------------------------------
    # Exibe itens adicionados
    # ------------------------------------------------------------------
    st.markdown("---")
    st.markdown("#### Itens Adicionados (salve antes de sair)")
    if not st.session_state["frota_temp"]:
        st.info("Nenhum item adicionado ainda.")
    else:
        for i, itm in enumerate(st.session_state["frota_temp"], start=1):
            with st.expander(f"Item {i}: {itm.get('tipo_bem','')}"):
                for k, v in itm.items():
                    st.write(f"**{k.replace('_',' ').capitalize()}:** {v or ''}")
                e, d = st.columns(2)
                if e.button(f"Editar {i}", key=f"e{i}"):
                    st.session_state["edit_index"] = i - 1
                if d.button(f"Excluir {i}", key=f"d{i}"):
                    st.session_state["frota_temp"].pop(i - 1)
                    st.success(f"Item {i} removido.")

    # ------------------------------------------------------------------
    # Salvar todos e redirecionar sem experimental
    # ------------------------------------------------------------------
    if st.session_state["frota_temp"]:
        st.markdown("---")
        if st.button("Salvar todos os itens", key="save_button", use_container_width=True):
            try:
                conn = sqlite3.connect("app/database/veiculos.db")
                cur = conn.cursor()
                query = """
                    INSERT INTO frota_2025 (
                        usuario_id, setor_id, data_preenchimento, tipo_bem, subtipo_bem,
                        placa, numero_chassi, renavam, numero_patrimonio, proprietario,
                        marca, modelo, ano_fabricacao, ano_modelo, cor, combustivel,
                        status, observacao
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """
                uid = usuario["id"]
                for itm in st.session_state["frota_temp"]:
                    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    vals = (
                      uid, setor, data,
                      itm["tipo_bem"], itm["subtipo_bem"], itm["placa"],
                      itm["numero_chassi"], itm["renavam"], itm["numero_patrimonio"],
                      itm["proprietario"], itm["marca"], itm["modelo"],
                      itm["ano_fabricacao"], itm["ano_modelo"], itm["cor"],
                      itm["combustivel"], itm["status"], itm["observacao"]
                    )
                    cur.execute(query, vals)
                conn.commit()
                conn.close()
                st.session_state["frota_temp"].clear()
                st.success("Todos os itens foram salvos com sucesso!")
                # Chama diretamente a página de exportação
                return
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
                if conn:
                    conn.rollback()
                    conn.close()
                st.session_state["frota_temp"].clear()
                st.warning("Lista temporária zerada devido a erro.")
