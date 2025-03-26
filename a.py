import pandas as pd
from fuzzywuzzy import process
import openpyxl

# Caminho da planilha original
arquivo_origem = "Veículos Maxifrota backup 02 2025_COMAG 1.xlsx"
arquivo_corrigido = "planilha_corrigida.xlsx"

# Lê todas as abas da planilha
planilhas = pd.read_excel(arquivo_origem, sheet_name=None)

# Extrai as abas relevantes
df_transacao = planilhas["transacao"]
print("Colunas da aba transacao:")
for col in df_transacao.columns:
    print(f"- '{col}'")
df_estrutura = planilhas["Estrutura"]

# Coluna com erros na transacao
coluna_errada = "Centro de Custo (UC)"

# Coluna com nomes corretos na estrutura
coluna_correta = "UORG"

# Coleta os valores únicos
nomes_errados = df_transacao[coluna_errada].astype(str).unique()
nomes_corretos = df_estrutura[coluna_correta].dropna().astype(str).unique()

# Mapeia os nomes errados para os corretos com fuzzy matching
mapa_correcao = {}
for nome in nomes_errados:
    melhor_correspondencia, score = process.extractOne(nome, nomes_corretos)
    if score >= 80:  # Ajuste esse valor se necessário
        mapa_correcao[nome] = melhor_correspondencia

# Aplica as correções
df_transacao[coluna_errada] = df_transacao[coluna_errada].astype(str).replace(mapa_correcao)

# Atualiza a aba no dicionário
planilhas["transacao"] = df_transacao

# Salva tudo em uma nova planilha
with pd.ExcelWriter(arquivo_corrigido, engine='openpyxl') as writer:
    for nome_aba, df in planilhas.items():
        df.to_excel(writer, sheet_name=nome_aba, index=False)

print("✅ Planilha corrigida gerada com sucesso!")
