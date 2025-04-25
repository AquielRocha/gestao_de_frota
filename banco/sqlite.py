import pandas as pd
from sqlalchemy import create_engine, text

# CONFIGURAÇÃO DA CONEXÃO PARA SQLITE
# Vai criar um banco local chamado 'gestao_de_frota.db' na mesma pasta
caminho_banco = 'app/database/frota.db'

# Caminho do arquivo Excel
caminho_arquivo = r've.xlsx'

# Lê o arquivo, pulando a primeira linha (header=1)
df = pd.read_excel(caminho_arquivo, header=1)

# Limpa espaços em branco nas colunas
df.columns = df.columns.str.strip()

# Mostra as colunas pra conferência
print("Colunas encontradas:", df.columns.tolist())

# Renomeia para bater com o banco
df = df.rename(columns={
    'Identificação': 'identificacao',
    'Proprietário': 'proprietario',
    'Lotação': 'lotacao',
    'Código (RENAVAM)': 'codigo_renavam',
    'Número Serie Chassi': 'numero_serie_chassi',
    'Fabricante': 'fabricante',
    'Modelo': 'modelo',
    'Ano Fabricação': 'ano_fabricacao',
    'Ano Modelo': 'ano_modelo',
    'Tipo Acoplamento': 'tipo_acoplamento',
    'Motorização': 'motorizacao',
    'Tipo de Bem': 'tipo_bem',
    'Subtipo do Bem': 'subtipo_bem',
    'Centro de Custo (UC)': 'centro_custo_uc',
    'Status': 'status',
    'Controle Desempenho': 'controle_desempenho',
    'Uso (KM)': 'uso_km',
    'Campos Adicionais': 'campos_adicionais',
    'Tipo Propriedade': 'tipo_propriedade',
    'Tipo Combustível': 'tipo_combustivel',
    'Data Aquisição': 'data_aquisicao',
    'Cor': 'cor',
    'Ordem (Nº Patrimônio)': 'ordem_num_patrimonio',
    'Observações': 'observacoes'
})

# Adiciona a coluna de ano
df['ano'] = 2024

# Remove a coluna 'Quant.' se existir
colunas_para_remover = ['Quant.', 'Quant___']
for coluna in colunas_para_remover:
    if coluna in df.columns:
        df = df.drop(columns=[coluna])

# Garante que só as colunas certas estão no DataFrame
colunas_esperadas = [
    'identificacao', 'proprietario', 'lotacao', 'codigo_renavam',
    'numero_serie_chassi', 'fabricante', 'modelo', 'ano_fabricacao',
    'ano_modelo', 'tipo_acoplamento', 'motorizacao', 'tipo_bem',
    'subtipo_bem', 'centro_custo_uc', 'status', 'controle_desempenho',
    'uso_km', 'campos_adicionais', 'tipo_propriedade', 'tipo_combustivel',
    'data_aquisicao', 'cor', 'ordem_num_patrimonio', 'observacoes', 'ano'
]
df = df[colunas_esperadas]

# Cria conexão com o SQLite
engine = create_engine(f'sqlite:///{caminho_banco}')

with engine.begin() as conn:
    # ATIVA FK no SQLite
    conn.execute(text('PRAGMA foreign_keys = ON'))

    # CRIAÇÃO DAS TABELAS SE NÃO EXISTIREM
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS setor (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        sigla TEXT NOT NULL
    );
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        cpf TEXT,
        email TEXT NOT NULL,
        senha TEXT NOT NULL,
        setor_codigo INTEGER,
        tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('admin', 'comum')),
        FOREIGN KEY (setor_codigo) REFERENCES setor(codigo)
    );
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS equipamentos (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL,
        identificacao TEXT,
        proprietario TEXT,
        lotacao TEXT,
        codigo_renavam TEXT,
        numero_serie_chassi TEXT,
        fabricante TEXT,
        modelo TEXT,
        ano_fabricacao INTEGER,
        ano_modelo INTEGER,
        tipo_acoplamento TEXT,
        motorizacao TEXT,
        tipo_bem TEXT,
        subtipo_bem TEXT,
        centro_custo_uc INTEGER NOT NULL,
        status TEXT,
        controle_desempenho TEXT,
        uso_km NUMERIC,
        campos_adicionais TEXT,
        tipo_propriedade TEXT,
        tipo_combustivel TEXT,
        data_aquisicao DATE,
        cor TEXT,
        ordem_num_patrimonio TEXT,
        observacoes TEXT,
        FOREIGN KEY (centro_custo_uc) REFERENCES setor(codigo)
    );
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS historico_atualizacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        equipamento_codigo INTEGER,
        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        acao TEXT,
        detalhes TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id),
        FOREIGN KEY (equipamento_codigo) REFERENCES equipamentos(codigo)
    );
    """))

    # 1. Inserir Setores
    setores_unicos = df['centro_custo_uc'].dropna().unique()
    for setor in setores_unicos:
        existe = conn.execute(
            text("SELECT 1 FROM setor WHERE nome = :nome"),
            {"nome": setor}
        ).fetchone()
        if not existe:
            conn.execute(
                text("INSERT INTO setor (nome, sigla) VALUES (:nome, :sigla)"),
                {"nome": setor, "sigla": setor[:5].upper()}
            )
    print("✅ Setores inseridos/validados com sucesso!")

    # 2. Inserir Usuários de Teste
    admin_username = 'admin_test'
    comum_username = 'user_test'

    conn.execute(
        text("""
            INSERT OR IGNORE INTO usuario (username, nome, cpf, email, senha, setor_codigo, tipo_usuario)
            VALUES (:username, :nome, :cpf, :email, :senha, :setor_codigo, 'admin')
        """),
        {
            "username": admin_username,
            "nome": "Administrador Teste",
            "cpf": "00000000191",
            "email": "admin@test.com",
            "senha": "admin123",
            "setor_codigo": 1
        }
    )

    conn.execute(
        text("""
            INSERT OR IGNORE INTO usuario (username, nome, cpf, email, senha, setor_codigo, tipo_usuario)
            VALUES (:username, :nome, :cpf, :email, :senha, :setor_codigo, 'comum')
        """),
        {
            "username": comum_username,
            "nome": "Usuario Comum Teste",
            "cpf": "00000000200",
            "email": "comum@test.com",
            "senha": "user123",
            "setor_codigo": 1
        }
    )
    print("✅ Usuários de teste criados!")

    # 3. Mapeia o nome do setor para o ID
    setores_db = conn.execute(text("SELECT codigo, nome FROM setor")).fetchall()
    mapa_setores = {nome: codigo for codigo, nome in setores_db}

    df['centro_custo_uc'] = df['centro_custo_uc'].map(mapa_setores)

    if df['centro_custo_uc'].isnull().any():
        print("🚨 Atenção: Existem setores na planilha que não foram encontrados no banco!")
        setores_nao_mapeados = df[df['centro_custo_uc'].isnull()]
        print(setores_nao_mapeados[['identificacao']])

        # Cria (ou usa) um setor padrão
        setor_padrao_nome = "Setor Genérico"
        setor_padrao_sigla = "GEN"

        setor_padrao = conn.execute(
            text("SELECT codigo FROM setor WHERE nome = :nome"),
            {"nome": setor_padrao_nome}
        ).fetchone()

        if not setor_padrao:
            conn.execute(
                text("INSERT INTO setor (nome, sigla) VALUES (:nome, :sigla)"),
                {"nome": setor_padrao_nome, "sigla": setor_padrao_sigla}
            )
            setor_padrao = conn.execute(
                text("SELECT codigo FROM setor WHERE nome = :nome"),
                {"nome": setor_padrao_nome}
            ).fetchone()

        codigo_setor_padrao = setor_padrao[0]

        df['centro_custo_uc'] = df['centro_custo_uc'].fillna(codigo_setor_padrao)
        print(f"✅ Setores não encontrados foram atribuídos ao setor padrão: {setor_padrao_nome} (ID {codigo_setor_padrao})")

    # 4. Inserir Equipamentos
    df.to_sql('equipamentos', con=conn.connection, if_exists='append', index=False)
    print("✅ Equipamentos inseridos com sucesso!")
