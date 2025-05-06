import streamlit as st
import pandas as pd, sqlite3, re
from datetime import datetime, date
from app.services.auth import check_user_logged_in

# ───────────────────────── helpers ─────────────────────────
DB = "app/database/frota.db"
def get_connection(): return sqlite3.connect(DB)

def get_equip_setor_ano(setor:int, ano:int)->pd.DataFrame:
    sql = "SELECT * FROM equipamentos WHERE centro_custo_uc=? AND ano=?"
    with get_connection() as con:
        return pd.read_sql(sql, con, params=(setor, ano))

def get_distinct(col:str)->list[str]:
    with get_connection() as con:
        return (
            pd.read_sql(f"SELECT DISTINCT {col} FROM equipamentos "
                        f"WHERE {col} IS NOT NULL", con)[col]
            .astype(str).dropna().sort_values().tolist()
        )

# map status → oficial
STATUS_MAP = {
    "novo": "Bem em perfeito estado, sem uso ou com uso muito recente, sem sinais de desgaste.",
    "bom": "Bem usado, mas em boas condições físicas e de funcionamento.",
    "regular": "Bem com sinais evidentes de uso, algum desgaste, mas ainda funcional.",
    "ocioso": "Bem em bom estado, mas sem uso por falta de necessidade ou planejamento.",
    "ocioso_ocioso": "Bem totalmente parado e sem previsão de uso. (Pode ser considerado para desfazimento)",
    "antieconomico": "Bem que gera mais custos de manutenção do que benefícios ou que é obsoleto.",
    "irrecuperavel": "Bem danificado ou inservível, sem possibilidade de recuperação ou reaproveitamento."
}
status_oficiais = sorted(set(STATUS_MAP.values()))

# anos para select
ANOS = [""] + list(reversed(range(1970, date.today().year+2)))

# ─────────────────────────  página ─────────────────────────
def run():
    #  CSS + barra busca
    st.markdown("""
    <style>
    :root{--bg:#f7fafc;--bg-card:#ffffff;--primary:#2d3748;--primary-light:#4a5568;
          --text:#2d3748;--border:#e2e8f0;--accent:#edf2f7;}
    div.stButton>button#save_button{background:var(--primary)!important;color:#fff!important;
        border-radius:5px!important;padding:10px 20px;font-weight:bold;}
    .frota-card{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;
        padding:10px;margin-bottom:12px;overflow:auto;max-height:600px;box-shadow:0 1px 2px rgba(15,23,42,.08);}
    .frota-table{width:100%;min-width:700px;border-collapse:collapse;font-size:15px;color:var(--text)}
    .frota-table th,.frota-table td{padding:8px;border:1px solid var(--border);text-align:left}
    .frota-table thead{background:var(--primary);color:#fff}
    .frota-table thead th{position:sticky;top:0;z-index:10;background:var(--primary)}
    .frota-table tbody tr:nth-child(odd){background:var(--accent)}
    .frota-table tbody tr:hover{background:var(--primary-light);color:#fff}
    </style>

    """, unsafe_allow_html=True)

    # usuário
    check_user_logged_in()
    usr   = st.session_state.user
    setor = usr["setor_codigo"]
    st.markdown(f"## Equipamentos da Unidade {usr.get('setor_nome','')}")

    # ---------------------- tabela 2024 ----------------------
    df24 = get_equip_setor_ano(setor, 2024)

    # descarta ident. que já estão na lista temp ou já inseridos em 2025
    if "frota_temp" not in st.session_state: st.session_state["frota_temp"]=[]
    ident_temp = {d["identificacao"] for d in st.session_state["frota_temp"]}
    ident_25   = set(get_equip_setor_ano(setor, 2025)["identificacao"].dropna().astype(str))
    df24 = df24[~df24["identificacao"].astype(str).isin(ident_temp|ident_25)]

    defaults = {c:"" for c in [
      "identificacao","codigo_renavam","numero_serie_chassi","ordem_num_patrimonio",
      "fabricante","modelo","ano_fabricacao","ano_modelo","tipo_bem","subtipo_bem",
      "tipo_propriedade","proprietario","controle_desempenho","uso_km","tipo_acoplamento",
      "motorizacao","tipo_combustivel","status","cor","campos_adicionais","observacoes"
    ]}

    if not df24.empty:
        st.markdown(" Equipamentos 2024 ainda NÃO migrados (Identificação ↓")
        st.markdown(f'<div class="frota-card">{df24[["identificacao","fabricante","modelo","ordem_num_patrimonio"]].rename(columns={"identificacao":"Identificação","ordem_num_patrimonio":"Patrimônio"}).to_html(index=False,classes="frota-table",border=0)}</div>',unsafe_allow_html=True)
        escolha = st.selectbox("Copiar dados de 2024", [""]+df24["identificacao"].astype(str).unique().tolist())
        if escolha:
            row=df24[df24["identificacao"]==escolha].iloc[0]
            for k in defaults:
                if k in row and pd.notna(row[k]): defaults[k]=str(row[k])

    # opções dinâmicas
    tipos      = get_distinct("tipo_bem")
    subtipos   = get_distinct("subtipo_bem")
    props      = get_distinct("proprietario")
    tipo_props = get_distinct("tipo_propriedade")
    controle_l = get_distinct("controle_desempenho")
    combust_l  = get_distinct("tipo_combustivel")
    acopl_l    = get_distinct("tipo_acoplamento")
    motor_l    = get_distinct("motorizacao")

    # ---------------------- formulário ----------------------
    st.markdown("---"); st.markdown("#### Adicionar / Editar equipamento 2025")
    st.markdown("""<div style="background:#fff8c4;padding:10px;border-left:5px solid #e6b800;border-radius:5px">
    <strong>Nº Patrimônio</strong> é obrigatório. Caso não exista, marque a caixa e justifique.</div>""",unsafe_allow_html=True)

    sem_patr = st.checkbox("Sem Nº Patrimônio (precisa justificar)")
    patr = "" if sem_patr else st.text_input("Número Patrimônio*", value=defaults["ordem_num_patrimonio"])
    justif = st.text_input("Justificativa*", value="") if sem_patr else ""

    with st.form("add_form", clear_on_submit=True):
        col1,col2 = st.columns(2)
        with col1:
            identificacao = st.text_input("Identificação / Placa*", value=defaults["identificacao"])
            fabricante    = st.text_input("Fabricante", value=defaults["fabricante"])
            modelo        = st.text_input("Modelo", value=defaults["modelo"])
            tipo_bem      = st.selectbox("Tipo de Bem", [""]+tipos, index=([""]+tipos).index(defaults["tipo_bem"]) if defaults["tipo_bem"] in tipos else 0)
            subtipo_bem   = st.selectbox("Subtipo de Bem", [""]+subtipos, index=([""]+subtipos).index(defaults["subtipo_bem"]) if defaults["subtipo_bem"] in subtipos else 0)
            proprietario  = st.selectbox("Proprietário", [""]+props, index=([""]+props).index(defaults["proprietario"]) if defaults["proprietario"] in props else 0)
            tipo_prop     = st.selectbox("Tipo Propriedade", [""]+tipo_props, index=([""]+tipo_props).index(defaults["tipo_propriedade"]) if defaults["tipo_propriedade"] in tipo_props else 0)
            tipo_acopl    = st.selectbox("Tipo Acoplamento", ["Não se aplica"]+acopl_l, index=(["Não se aplica"]+acopl_l).index(defaults["tipo_acoplamento"]) if defaults["tipo_acoplamento"] in acopl_l else 0)
            motorizacao   = st.selectbox("Motorização", ["Não se aplica"]+motor_l, index=(["Não se aplica"]+motor_l).index(defaults["motorizacao"]) if defaults["motorizacao"] in motor_l else 0)
        with col2:
            renavam  = st.text_input("RENAVAM", value=defaults["codigo_renavam"])
            chassi   = st.text_input("Chassi",  value=defaults["numero_serie_chassi"])
            ano_fab  = st.selectbox("Ano Fabricação", ANOS, index=ANOS.index(int(defaults["ano_fabricacao"])) if defaults["ano_fabricacao"].isdigit() else 0)
            ano_mod  = st.selectbox("Ano Modelo", ANOS, index=ANOS.index(int(defaults["ano_modelo"])) if defaults["ano_modelo"].isdigit() else 0)
            cor      = st.text_input("Cor", value=defaults["cor"])
            lotacao  = st.text_input("Lotação (Centro de Custo)", value=str(setor), disabled=True)
        controle = st.selectbox("Controle Desempenho", ["Não se aplica"]+controle_l, index=(["Não se aplica"]+controle_l).index(defaults["controle_desempenho"]) if defaults["controle_desempenho"] in controle_l else 0)
        uso_km   = st.text_input("Uso (KM/Horas)", value=defaults["uso_km"])
        combust  = st.selectbox("Tipo Combustível", [""]+combust_l, index=([""]+combust_l).index(defaults["tipo_combustivel"]) if defaults["tipo_combustivel"] in combust_l else 0)
        status   = st.selectbox("Status", [""]+status_oficiais, index=([""]+status_oficiais).index(defaults["status"]) if defaults["status"] in status_oficiais else 0)

        campos_add = st.text_area("Campos Adicionais", value=defaults["campos_adicionais"])
        obs        = st.text_area("Observações", value=defaults["observacoes"])

        add = st.form_submit_button("Adicionar à lista")

    # --------------- validação & append ---------------
    if add:
        if not identificacao.strip():
            st.error("Identificação é obrigatória.")
        elif not sem_patr and not patr.strip():
            st.error("Patrimônio é obrigatório.")
        elif sem_patr and not justif.strip():
            st.error("Justifique ausência do patrimônio.")
        else:
            st.session_state.frota_temp.append(dict(
                identificacao=identificacao,
                codigo_renavam=renavam or "Não se aplica",
                numero_serie_chassi=chassi or "Não se aplica",
                ordem_num_patrimonio= patr if not sem_patr else f"JUST: {justif}",
                fabricante=fabricante or "Não informado",
                modelo=modelo or "Não informado",
                tipo_bem=tipo_bem, subtipo_bem=subtipo_bem,
                proprietario=proprietario, tipo_propriedade=tipo_prop,
                tipo_acoplamento=tipo_acopl, motorizacao=motorizacao,
                controle_desempenho=controle, uso_km=uso_km or "0",
                tipo_combustivel=combust, status=status, cor=cor or "Não informado",
                campos_adicionais=campos_add, observacoes=obs,
                ano_fabricacao=str(ano_fab) if ano_fab else "",
                ano_modelo=str(ano_mod) if ano_mod else ""
            ))
            st.success("Item colocado na lista.")

    # --------------- lista temp ---------------
    st.markdown("---"); st.markdown("#### Itens na lista")
    for i,it in enumerate(st.session_state.frota_temp,1):
        st.write(f"{i}. {it['identificacao']} | Patrimônio: {it['ordem_num_patrimonio']}")

    # --------------- salvar ---------------
    if st.session_state.frota_temp:
        if st.button("Salvar todos os itens", key="save_button"):
            try:
                with get_connection() as con:
                    sql_eqp = """
                    INSERT INTO equipamentos (
                      ano, centro_custo_uc, identificacao, codigo_renavam,
                      numero_serie_chassi, ordem_num_patrimonio, fabricante,
                      modelo, tipo_bem, subtipo_bem, proprietario, tipo_acoplamento,
                      motorizacao, controle_desempenho, uso_km, campos_adicionais,
                      tipo_propriedade, tipo_combustivel, status, cor, observacoes,
                      data_aquisicao, ano_fabricacao, ano_modelo
                    ) VALUES (2025,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """
                    sql_log = "INSERT INTO historico_atualizacoes (usuario_id,equipamento_codigo,acao,detalhes) VALUES (?,?, 'insercao',?)"
                    uid, hoje = usr["id"], datetime.today().date()

                    for it in st.session_state.frota_temp:
                        cur = con.execute(sql_eqp, (
                            setor, it["identificacao"], it["codigo_renavam"],
                            it["numero_serie_chassi"], it["ordem_num_patrimonio"],
                            it["fabricante"], it["modelo"], it["tipo_bem"], it["subtipo_bem"],
                            it["proprietario"], it["tipo_acoplamento"], it["motorizacao"],
                            it["controle_desempenho"], it["uso_km"], it["campos_adicionais"],
                            it["tipo_propriedade"], it["tipo_combustivel"], it["status"],
                            it["cor"], it["observacoes"], hoje,
                            it["ano_fabricacao"] or None, it["ano_modelo"] or None
                        ))
                        eid = cur.lastrowid
                        con.execute(sql_log, (uid, eid, f"inclusão por usuário {uid}"))

                    con.commit()
                st.session_state.frota_temp.clear()
                st.success("Itens salvos – tabela 2024 atualizada.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
