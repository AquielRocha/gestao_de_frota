import sqlite3
import streamlit as st
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_connection(db_path="app/database/veiculos.db"):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # Cria tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            setor_id TEXT
        )
    """)
    # Cria tabela mínima para frota (se não existir)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            centro_custo TEXT,
            gerencia_regional TEXT,
            tipo_bem TEXT,
            subtipo_bem TEXT,
            placa TEXT,
            numero_chassi TEXT,
            renavam TEXT,
            numero_patrimonio TEXT,
            proprietario TEXT,
            marca TEXT,
            modelo TEXT,
            cor TEXT,
            combustivel TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(nome: str, email: str, senha: str, setor_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM usuario WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False
    senha_hash = hash_password(senha)
    cursor.execute("""
        INSERT INTO usuario (nome, email, senha_hash, setor_id)
        VALUES (?, ?, ?, ?)
    """, (nome, email, senha_hash, setor_id))
    conn.commit()
    conn.close()
    return True

def login_user(email: str, senha: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT senha_hash FROM usuario WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        stored_hash = row[0]
        return verify_password(senha, stored_hash)
    return False

def get_user_info(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, setor_id FROM usuario WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nome": row[1], "email": row[2], "setor_id": row[3]}
    return None

def check_user_logged_in():
    if "user" not in st.session_state or st.session_state.user is None:
        st.warning("Você não está logado. Faça login para acessar esta página.")
        st.stop()

def get_setor_options():
    """
    Retorna uma lista única com os valores distintos da coluna 'centro_custo'
    da tabela 'frota', aplicando um strip para eliminar espaços extras.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT centro_custo FROM frota")
    rows = cursor.fetchall()
    conn.close()
    # Remove valores None, aplica strip e utiliza set para garantir unicidade
    options = list({row[0].strip() for row in rows if row[0] is not None})
    options.sort()  # Ordena as opções, se desejado
    return options
