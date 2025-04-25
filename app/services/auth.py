import sqlite3
from hashlib import sha256
from app.services.db import get_connection
import streamlit as st   # pra check_user_logged_in

# ---------- helpers ----------
def _hash_pwd(pwd: str) -> str:
    return sha256(pwd.encode()).hexdigest()


# ---------- login / cadastro ----------
def login_user(cpf: str, pwd: str) -> bool:
    sql = "SELECT id FROM usuario WHERE cpf = ? AND senha = ?"
    with get_connection() as con:
        cur = con.execute(sql, (cpf, _hash_pwd(pwd)))
        return cur.fetchone() is not None


def create_user(nome: str, cpf: str, pwd: str,
                email: str, setor_codigo: int,
                tipo: str = "comum") -> bool:
    sql = """
        INSERT INTO usuario (nome, cpf, email, senha,
                             setor_codigo, username, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as con:
            con.execute(sql, (
                nome, cpf, email, _hash_pwd(pwd),
                setor_codigo, cpf, tipo
            ))
        return True
    except sqlite3.IntegrityError:
        return False

def get_user_info(cpf: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, setor_codigo, tipo_usuario FROM usuario WHERE cpf = ?", (cpf,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "nome": row[1],
            "cpf": row[2],
            "setor_codigo": row[3],
            "tipo_usuario": row[4]  # <<-- ISSO É MUITO IMPORTANTE!!!
        }
    return None


def get_setor_options() -> list[dict]:
    with get_connection() as con:
        cur = con.execute(
            "SELECT codigo, nome, sigla FROM setor ORDER BY nome"
        )
        return [dict(r) for r in cur.fetchall()]


def check_user_logged_in():
    if "user" not in st.session_state or st.session_state.user is None:
        st.warning("Tu não tá logado, chefia. Faz login aí primeiro.")
        st.stop()


