# Radar Ativos API

API para análise de ações e FIIs, focada em investimentos brasileiros. Permite consultar indicadores, gerenciar carteiras, registrar transações e obter recomendações quantitativas.

Um front-end para utilizar esta API está disponível em: [https://github.com/marco-ostaska/radar-ui](https://github.com/marco-ostaska/radar-ui)

## Funcionalidades

- Consulta de dados resumidos e detalhados de ações e FIIs
- Gerenciamento de carteiras (ações e FIIs)
- Registro e atualização de transações
- Consulta e administração de indicadores de mercado
- Recomendações quantitativas baseadas em critérios objetivos
- Integração com fontes externas (Banco Central, Investidor10, Yahoo Finance)

## Endpoints Principais

- `/acoes/radar`: Retorna informações resumidas de uma ação (ticker, cotação, DY, potencial, score, recomendação de compra)
- `/carteira`: Gerencia carteiras de ações e FIIs (adicionar, remover, listar)
- `/transacoes`: Adiciona, lista, atualiza e remove transações de ativos
- `/indicadores`: Consulta e administra indicadores de mercado
- `/indices`: Consulta índices econômicos (IPCA, Selic, etc.)

> A documentação interativa (Swagger) estará disponível em `http://localhost:8000/docs` após subir a API.

## Banco de Dados

> **Importante:** O banco de dados precisa ser criado antes de subir a aplicação.

### Como criar o banco de dados

Execute o comando abaixo para criar toda a estrutura do banco:

```sh
sqlite3 radar_ativos.db < sqlite/create_radar_db.sql
```

O projeto utiliza um banco SQLite local (`radar_ativos.db`) com a seguinte arquitetura:

- **tipos**: Tipos de ativos (ex: ação, FII).
- **ativos**: Lista de ativos (tickers) e seus tipos.
- **indices_banco_central**: Índices econômicos (ex: selic, ipca, ipca_atual).
- **transacoes_acoes**: Registro de transações de ações (compra, venda, quantidade, preço, data, ativo).
- **transacoes_fii** / **transacoes_fiis**: Registro de transações de FIIs.
- **carteira_acoes**: Carteira consolidada de ações por ticker.
- **carteira_fiis**: Carteira consolidada de FIIs por ticker.
- **notas_acoes**: Notas atribuídas a ações por carteira (carteira_id, ticker, nota de 0 a 100).
- **notas_fiis**: Notas atribuídas a FIIs por carteira (carteira_id, ticker, nota de 0 a 100).

As tabelas de transações armazenam o histórico de operações do usuário, enquanto as tabelas de carteira consolidam os saldos atuais. A tabela de índices permite integração e atualização automática de indicadores econômicos.

As relações entre as tabelas são feitas principalmente via o campo `ticker` e tipos de ativos.

## Instalação e Execução

### Via Docker

```sh
docker build -t radar-ativos-api .
docker run -p 8000:8000 radar-ativos-api
```

### Localmente

```sh
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## Redis

Esta API faz uso do Redis para cache de dados e otimização de performance, reduzindo o tempo de resposta em consultas frequentes e evitando sobrecarga em integrações externas.

Para rodar o Redis localmente via Docker:

```sh
docker run -d --name redis-local -p 6379:6379 redis:7-alpine redis-server --appendonly yes
```

> O Redis deve estar em execução antes de iniciar a API.

---

## Disclaimer

Esta API foi desenvolvida exclusivamente para fins de estudo e testes. Ela faz uso de dados de terceiros, que podem mudar a qualquer momento e comprometer seu funcionamento. Não há qualquer garantia sobre a precisão, disponibilidade ou continuidade dos dados fornecidos. O autor não se responsabiliza por eventuais perdas, danos ou decisões tomadas com base nas informações retornadas por esta API. **Não utilize esta API para análises financeiras reais ou decisões de investimento.**
