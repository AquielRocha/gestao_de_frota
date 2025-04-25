import pandas as pd
from sqlalchemy import create_engine, text

# CONFIGURAÇÃO DA CONEXÃO
usuario = 'postgres'
senha = 'asd'
host = 'localhost'
porta = '5432'  # Confirma se é 5432 ou 6000 no teu ambiente
banco = 'comaglab'

# Caminho do arquivo Excel
caminho_arquivo = r'C:\Users\Faculdade\Desktop\ICMBIO\gestao_de_frota\ve.xlsx'

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

# Cria conexão com o banco
engine = create_engine(f'postgresql://{usuario}:{senha}@{host}:{porta}/{banco}')

with engine.begin() as conn:
    # 1. Inserir Setores
    setores_unicos = df['centro_custo_uc'].dropna().unique()
    for setor in setores_unicos:
        existe = conn.execute(
            text("SELECT 1 FROM frota.setor WHERE nome = :nome"),
            {"nome": setor}
        ).fetchone()
        if not existe:
            conn.execute(
                text("INSERT INTO frota.setor (nome, sigla) VALUES (:nome, :sigla)"),
                {"nome": setor, "sigla": setor[:5].upper()}
            )
    print("✅ Setores inseridos/validados com sucesso!")

    # 2. Inserir Usuários de Teste
    admin_username = 'admin_test'
    comum_username = 'user_test'

    conn.execute(
        text("""
            INSERT INTO frota.usuario (username, nome, cpf, email, senha, setor_codigo, tipo_usuario)
            VALUES (:username, :nome, :cpf, :email, :senha, :setor_codigo, 'admin')
            ON CONFLICT (username) DO NOTHING
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
            INSERT INTO frota.usuario (username, nome, cpf, email, senha, setor_codigo, tipo_usuario)
            VALUES (:username, :nome, :cpf, :email, :senha, :setor_codigo, 'comum')
            ON CONFLICT (username) DO NOTHING
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
    setores_db = conn.execute(text("SELECT codigo, nome FROM frota.setor")).fetchall()
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
            text("SELECT codigo FROM frota.setor WHERE nome = :nome"),
            {"nome": setor_padrao_nome}
        ).fetchone()

        if not setor_padrao:
            # Se não existir, cria
            conn.execute(
                text("INSERT INTO frota.setor (nome, sigla) VALUES (:nome, :sigla)"),
                {"nome": setor_padrao_nome, "sigla": setor_padrao_sigla}
            )
            setor_padrao = conn.execute(
                text("SELECT codigo FROM frota.setor WHERE nome = :nome"),
                {"nome": setor_padrao_nome}
            ).fetchone()

        codigo_setor_padrao = setor_padrao[0]

        # Agora substitui todos os NaN pelo setor padrão
        df['centro_custo_uc'] = df['centro_custo_uc'].fillna(codigo_setor_padrao)
        print(f"✅ Setores não encontrados foram atribuídos ao setor padrão: {setor_padrao_nome} (ID {codigo_setor_padrao})")

    # 4. Inserir Equipamentos
    df.to_sql('equipamentos', con=conn, schema='frota', if_exists='append', index=False)
    print("✅ Equipamentos inseridos com sucesso!")
