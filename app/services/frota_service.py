import sqlite3

def inserir_veiculo(usuario_id, setor_id, tipo_bem, subtipo_bem, placa, numero_chassi,
                    renavam, numero_patrimonio, proprietario, marca, modelo,
                    ano_fabricacao, ano_modelo, cor, combustivel, status,
                    observacao, adicionar_mais):
    conn = sqlite3.connect("app/database/veiculos.db")
    conn.execute('''
        INSERT INTO frota_2025 (
            usuario_id, setor_id, tipo_bem, subtipo_bem, placa, numero_chassi,
            renavam, numero_patrimonio, proprietario, marca, modelo,
            ano_fabricacao, ano_modelo, cor, combustivel, status,
            observacao, adicionar_mais
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (usuario_id, setor_id, tipo_bem, subtipo_bem, placa, numero_chassi,
          renavam, numero_patrimonio, proprietario, marca, modelo,
          ano_fabricacao, ano_modelo, cor, combustivel, status,
          observacao, adicionar_mais))
    conn.commit()
    conn.close()
