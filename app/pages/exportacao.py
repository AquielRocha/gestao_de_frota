import streamlit as st
import sqlite3
import pandas as pd
import io
from app.services.auth import check_user_logged_in

def export_data_to_excel(db_path="app/database/veiculos.db"):
    """
    Lê as tabelas 'frota' e 'frota_2025' do banco SQLite e gera um arquivo Excel
    com duas abas (frota e frota_2025) de forma estilizada.
    Retorna os bytes do arquivo em memória.
    """

    # Conecta ao banco e lê as tabelas
    conn = sqlite3.connect(db_path)
    df_frota = pd.read_sql_query("SELECT * FROM frota", conn)
    df_frota_2025 = pd.read_sql_query("SELECT * FROM frota_2025", conn)
    conn.close()

    # Cria um buffer em memória para o Excel
    output = io.BytesIO()

    # Abre o ExcelWriter com engine xlsxwriter
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escreve a planilha frota e estiliza
        df_frota.to_excel(
            writer,
            sheet_name='frota',
            index=False,
            startrow=1,      # Deixa uma linha para o cabeçalho manual
            header=False
        )
        # Obtemos referências para aplicar estilo
        workbook  = writer.book
        worksheet = writer.sheets['frota']

        # Formato do cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'middle',
            'align': 'center',
            'fg_color': '#D7E4BC',   # Cor de fundo (verde claro)
            'border': 1
        })

        # Formato padrão das células (dados)
        cell_format = workbook.add_format({
            'border': 1,
            'valign': 'top'
        })

        # Escreve o cabeçalho manualmente, aplicando o header_format
        for col_num, col_name in enumerate(df_frota.columns):
            worksheet.write(0, col_num, col_name, header_format)

        # Ajusta largura das colunas dinamicamente
        for i, col in enumerate(df_frota.columns):
            # Tamanho máximo entre o nome da coluna e o maior valor daquela coluna
            col_width = max(
                df_frota[col].astype(str).map(len).max(),
                len(col)
            )
            # Dá um pequeno acréscimo (2) para folga
            worksheet.set_column(i, i, col_width + 2, cell_format)

        # --------------------------------------------------------------------
        # Repetimos o mesmo processo para a planilha frota_2025
        df_frota_2025.to_excel(
            writer,
            sheet_name='frota_2025',
            index=False,
            startrow=1,
            header=False
        )
        worksheet_2025 = writer.sheets['frota_2025']

        # Escreve o cabeçalho manualmente
        for col_num, col_name in enumerate(df_frota_2025.columns):
            worksheet_2025.write(0, col_num, col_name, header_format)

        # Ajusta largura das colunas dinamicamente
        for i, col in enumerate(df_frota_2025.columns):
            col_width = max(
                df_frota_2025[col].astype(str).map(len).max(),
                len(col)
            )
            worksheet_2025.set_column(i, i, col_width + 2, cell_format)

    # Recupera o conteúdo binário do arquivo Excel
    excel_data = output.getvalue()
    return excel_data

def run():
    # Checa se o usuário está logado
    check_user_logged_in()

    st.title("Exportação do Sistema")
    st.write("Nesta página, você pode exportar os dados de Gestão de Frota para Excel com uma leve estilização.")

    # Botão para exportar
    if st.button("Gerar arquivo Excel"):
        xlsx_file = export_data_to_excel()
        # Cria um botão de download
        st.download_button(
            label="Baixar dados em Excel",
            data=xlsx_file,
            file_name="export_frota.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
