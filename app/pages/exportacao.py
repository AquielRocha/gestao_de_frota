import streamlit as st
import sqlite3, pandas as pd, io
from app.services.auth import check_user_logged_in

DB_PATH = "app/database/frota.db"

# ───────── helpers ─────────
def ler_equipamentos(ano:int, where:str="", params:tuple=()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql(f"SELECT * FROM equipamentos WHERE ano=? {where}", con,
                           params=(ano,*params))

def montar_excel(planilhas: dict[str, pd.DataFrame]) -> bytes:
    """planilhas = {"nome_aba": df, ...}  →  bytes .xlsx"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as wr:
        wb = wr.book
        header_fmt = wb.add_format({
            "bold": True, "fg_color": "#D7E4BC",
            "align": "center", "valign": "vcenter", "border":1
        })
        cell_fmt   = wb.add_format({"border":1, "valign":"top"})

        for aba, df in planilhas.items():
            df.to_excel(wr, sheet_name=aba, index=False, startrow=1, header=False)
            ws = wr.sheets[aba]

            for col, nome in enumerate(df.columns):
                ws.write(0, col, nome, header_fmt)
                largura = max(len(nome), df.iloc[:, col].astype(str).map(len).max()) + 2
                ws.set_column(col, col, largura, cell_fmt)
    return buf.getvalue()

# ───────── página ─────────
def run():
    check_user_logged_in()
    user = st.session_state.user

    st.title("📤 Exportação de Equipamentos")

    if user["tipo_usuario"] == "admin":
        st.info("Você é **administrador** — o arquivo terá duas abas: 2024 e 2025 (todos os dados).")
    else:
        st.info("Você é **usuário comum** — o arquivo terá apenas seus equipamentos de 2025.")

    if st.button("Gerar arquivo Excel"):
        try:
            if user["tipo_usuario"] == "admin":
                df24 = ler_equipamentos(2024)
                df25 = ler_equipamentos(2025)
                if df24.empty and df25.empty:
                    st.warning("Não há registros em 2024 nem 2025.")
                    return
                xlsx = montar_excel({"equipamentos_2024": df24,
                                     "equipamentos_2025": df25})
                nome = "equipamentos_2024_2025_COMPLETO.xlsx"

            else:  # comum
                df25 = ler_equipamentos(2025, "AND centro_custo_uc=?", (user["setor_codigo"],))
                if df25.empty:
                    st.warning("Você não possui registros de 2025.")
                    return
                xlsx = montar_excel({f"equipamentos_{user['setor_codigo']}_2025": df25})
                nome = f"equipamentos_2025_setor_{user['setor_codigo']}.xlsx"

            st.download_button("📥 Baixar Excel", xlsx, nome,
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"Erro ao gerar arquivo: {e}")
