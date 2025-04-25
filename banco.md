# Documentação do Banco de Dados - Sistema de Gestão de Frota

## SCHEMA
`frota`

---

## Tabelas

### 1. Tabela `setor`
| Coluna  | Tipo  | Descrição |
|:--------|:------|:----------|
| codigo  | SERIAL (PK) | Identificador único do setor (Centro de Custo) |
| nome    | TEXT  | Nome do setor |
| sigla   | TEXT  | Sigla abreviada do setor |

**Descrição:**
Cadastro dos setores (centros de custo). Cada equipamento e usuário está vinculado a um setor.

---

### 2. Tabela `usuario`
| Coluna        | Tipo   | Descrição |
|:--------------|:-------|:----------|
| id            | SERIAL (PK) | Identificador único do usuário |
| username      | TEXT (UNIQUE) | Nome de login do usuário |
| senha         | TEXT | Senha criptografada |
| setor_codigo  | INTEGER (FK -> setor.codigo) | Setor ao qual o usuário pertence |
| tipo_usuario  | TEXT ('admin' ou 'comum') | Define o nível de acesso do usuário |

**Descrição:**
Usuários do sistema, vinculados a setores. Admins gerenciam tudo, usuários comuns apenas seu próprio setor.

---

### 3. Tabela `equipamentos`
| Coluna               | Tipo   | Descrição |
|:----------------------|:-------|:----------|
| codigo                | SERIAL (PK) | Identificador único do equipamento |
| ano                   | INTEGER | Ano de referência do cadastro |
| identificacao         | TEXT | Identificação do equipamento |
| fabricante            | TEXT | Fabricante |
| modelo                | TEXT | Modelo |
| tipo_bem              | TEXT | Tipo de bem |
| subtipo_bem           | TEXT | Subtipo |
| centro_custo_uc       | INTEGER (FK -> setor.codigo) | Setor dono do equipamento |
| status                | TEXT | Status (ativo, inativo etc) |
| controle_desempenho   | TEXT | Controle de desempenho |
| uso_km                | NUMERIC | Quilometragem |
| campos_adicionais     | TEXT | Informações adicionais |
| tipo_propriedade      | TEXT | Tipo de propriedade |
| tipo_combustivel      | TEXT | Tipo de combustível |
| data_aquisicao        | DATE | Data de aquisição |
| cor                   | TEXT | Cor do equipamento |
| ordem_num_patrimonio  | TEXT | Número de patrimônio |
| observacoes           | TEXT | Observações gerais |

**Descrição:**
Todos os equipamentos cadastrados no sistema, com controle anual para gestão de histórico.

---

### 4. Tabela `historico_atualizacoes`
| Coluna               | Tipo   | Descrição |
|:----------------------|:-------|:----------|
| id                    | SERIAL (PK) | Identificador da ação |
| usuario_id            | INTEGER (FK -> usuario.id) | Usuário que fez a alteração |
| equipamento_codigo    | INTEGER (FK -> equipamentos.codigo) | Equipamento alterado |
| data_atualizacao      | TIMESTAMP | Data da atualização |
| acao                  | TEXT | Tipo de ação (insercao, atualizacao, exclusao) |
| detalhes              | TEXT | Detalhes adicionais |

**Descrição:**
Rastreia quem fez alterações nos equipamentos.

---

## Fluxo de Funcionamento

### 1. Cadastro Inicial
- Admin cadastra setores.
- Admin cadastra usuários vinculados aos setores.

### 2. Importação de Equipamentos
- Planilha é carregada.
- Adiciona-se o ano de referência (ex: 2024).
- Dados são inseridos na tabela `equipamentos`.

### 3. Login e Acesso
- Usuário comum: visualiza apenas equipamentos do seu setor no ano corrente.
- Admin: visualiza todos os equipamentos de todos os setores e anos.

Exemplo de consulta:
```sql
SELECT * FROM frota.equipamentos
WHERE centro_custo_uc = (SELECT setor_codigo FROM frota.usuario WHERE username = 'usuario_logado')
  AND ano = 2024;
```

### 4. Atualização Anual
- Copia registros de um ano para o próximo:

```sql
INSERT INTO frota.equipamentos (...)
SELECT 2025, ... FROM frota.equipamentos WHERE ano = 2024;
```

### 5. Controle de Alteracoes
- Cada alteração de equipamento é registrada em `historico_atualizacoes`.

---

## Resumo Visual

```text
[Admin cria setores] -> [Admin cria usuários] -> [Importa equipamentos]

Usuário loga ->
    Se ADMIN: vê todos
    Se COMUM: vê apenas seu setor

Usuário atualiza ano a ano -> Histórico registra alterações
```

