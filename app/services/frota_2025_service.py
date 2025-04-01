# app/services/frota_service.py

import sqlite3

def get_connection(db_path="app/database/veiculos.db"):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn

def get_veiculos_by_setor_ano(setor):
    """
    Retorna todas as colunas dos veículos da tabela 'frota' cujo
    'centro_custo' seja igual ao setor informado.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM frota_2025 WHERE setor_id = ?", (setor,))
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return rows, columns
