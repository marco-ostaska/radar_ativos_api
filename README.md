# Radar Ativos API

API para gerenciamento de carteiras de investimentos, incluindo ações e FIIs.

## Funcionalidades

- Gerenciamento de carteiras
- Registro de transações de ações e FIIs
- Cálculo de métricas de investimento
- Recomendações de trading baseadas em indicadores

## Estrutura do Banco de Dados

### Tabelas Principais

#### 1. Tabela `tipos`
Armazena os tipos de ativos e suas características.
- `tipo` (TEXT, PK): Tipo do ativo
- `spread` (INTEGER): Spread associado ao tipo
- `risco_operacional` (INTEGER): Nível de risco operacional

#### 2. Tabela `ativos`
Cadastro de todos os ativos disponíveis.
- `ticker` (TEXT, PK): Código do ativo
- `tipo` (TEXT, FK): Referência à tabela `tipos`

#### 3. Tabela `transacoes_acoes`
Registro de todas as transações de ações.
- `id` (INTEGER, PK): Identificador único
- `ticker` (TEXT, FK): Código da ação
- `data_transacao` (TEXT): Data da transação
- `tipo_transacao` (TEXT): Tipo (COMPRA, VENDA)
- `preco` (REAL): Preço unitário
- `quantidade` (INTEGER): Quantidade de ações
- `data_atualizacao` (TEXT): Data da última atualização

#### 4. Tabela `transacoes_fiis`
Registro de todas as transações de FIIs.
- `id` (INTEGER, PK): Identificador único
- `ticker` (TEXT, FK): Código do FII
- `data_transacao` (TEXT): Data da transação
- `tipo_transacao` (TEXT): Tipo (COMPRA, VENDA)
- `preco` (REAL): Preço unitário
- `quantidade` (INTEGER): Quantidade de cotas
- `data_atualizacao` (TEXT): Data da última atualização

#### 5. Tabela `carteira_acoes`
Resumo da carteira de ações.
- `ticker` (TEXT, PK): Código da ação
- `quantidade_total` (INTEGER): Quantidade total em carteira
- `preco_medio` (REAL): Preço médio de compra
- `total_investido` (REAL): Valor total investido
- `data_atualizacao` (TEXT): Data da última atualização

#### 6. Tabela `carteira_fiis`
Resumo da carteira de FIIs.
- `ticker` (TEXT, PK): Código do FII
- `quantidade_total` (INTEGER): Quantidade total em carteira
- `preco_medio` (REAL): Preço médio de compra
- `total_investido` (REAL): Valor total investido
- `data_atualizacao` (TEXT): Data da última atualização

#### 7. Tabela `indices_banco_central`
Armazena índices econômicos.
- `indice` (TEXT, PK): Nome do índice
- `valor` (REAL): Valor atual do índice
- `data_atualizacao` (TEXT): Data da última atualização

### Índices
- `idx_transacoes_acoes_ticker`: Índice para busca por ticker em transações de ações
- `idx_transacoes_acoes_data`: Índice para busca por data em transações de ações
- `idx_transacoes_fiis_ticker`: Índice para busca por ticker em transações de FIIs
- `idx_transacoes_fiis_data`: Índice para busca por data em transações de FIIs

### Triggers
- `update_transacoes_acoes_timestamp`: Atualiza data_atualizacao após modificação em transacoes_acoes
- `update_transacoes_fiis_timestamp`: Atualiza data_atualizacao após modificação em transacoes_fiis

## Requisitos

- Python 3.8+
- SQLite3

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/marco-ostaska/radar_ativos_api.git
cd radar_ativos_api
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Inicialize o banco de dados:
```bash
python sqlite/init_transacoes.py
```

## Executando a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Documentação da API

### Transações de Ações

#### Listar Transações
```
GET /transacoes/acoes/listar?carteira_id=1
```

#### Adicionar Transação
```
POST /transacoes/acoes/adicionar
Parâmetros:
- carteira_id: ID da carteira
- ticker: Código da ação (ex: PETR4)
- quantidade: Quantidade de ações
- preco: Preço unitário
- tipo: COMPRA ou VENDA
- data: Data da transação (dd/mm/yyyy)
```

#### Atualizar Transação
```
PUT /transacoes/acoes/atualizar/{transacao_id}
Parâmetros:
- carteira_id: ID da carteira
- ticker: Código da ação
- quantidade: Quantidade de ações
- preco: Preço unitário
- tipo: COMPRA ou VENDA
- data: Data da transação (dd/mm/yyyy)
```

#### Deletar Transação
```
DELETE /transacoes/acoes/deletar/{transacao_id}?carteira_id=1
```

### Transações de FIIs

#### Listar Transações
```
GET /transacoes/fii/listar?carteira_id=1
```

#### Adicionar Transação
```
POST /transacoes/fii/adicionar
Parâmetros:
- carteira_id: ID da carteira
- ticker: Código do FII (ex: HGLG11)
- quantidade: Quantidade de cotas
- preco: Preço unitário
- tipo: COMPRA ou VENDA
- data: Data da transação (dd/mm/yyyy)
```

#### Atualizar Transação
```
PUT /transacoes/fii/atualizar/{transacao_id}
Parâmetros:
- carteira_id: ID da carteira
- ticker: Código do FII
- quantidade: Quantidade de cotas
- preco: Preço unitário
- tipo: COMPRA ou VENDA
- data: Data da transação (dd/mm/yyyy)
```

#### Deletar Transação
```
DELETE /transacoes/fii/deletar/{transacao_id}?carteira_id=1
```

### Carteira

#### Visualizar Carteira de Ações
```
GET /carteira/acoes?carteira_id=1
```

#### Visualizar Carteira de FIIs
```
GET /carteira/fii?carteira_id=1
```

## Docker

Para executar a API usando Docker:

```bash
docker build -t radar-ativos-api .
docker run -p 8000:8000 radar-ativos-api
```

## Licença

Este projeto está sob a licença MIT. 