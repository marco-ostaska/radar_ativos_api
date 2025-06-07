# Instruções para Desenvolvimento da UI

## Contexto
Este é um projeto de interface para o Radar Ativos API, um sistema de gerenciamento de carteiras de investimentos. A API já está desenvolvida e documentada no repositório `radar_ativos_api`.

## Requisitos da UI

### 1. Páginas Principais

#### Dashboard
- Visão geral da carteira
- Gráficos de distribuição de ativos
- Resumo de ganhos/perdas
- Indicadores principais

#### Carteira de Ações
- Lista de ações com:
  - Ticker
  - Quantidade
  - Preço médio
  - Preço atual
  - Variação
  - Valor investido
  - Lucro/Prejuízo
  - Recomendações de trading
- Filtros por:
  - Ticker
  - Recomendação
  - Variação

#### Carteira de FIIs
- Lista de FIIs com:
  - Ticker
  - Quantidade
  - Preço médio
  - Preço atual
  - Variação
  - Valor investido
  - Lucro/Prejuízo
  - DY
  - P/VP
- Filtros por:
  - Ticker
  - Variação
  - DY

#### Transações
- Aba para Ações
- Aba para FIIs
- Em cada aba:
  - Lista de transações
  - Formulário para adicionar transação
  - Opções para editar/deletar transações

### 2. Funcionalidades

#### Adicionar Transação
- Formulário com:
  - Seleção de tipo (Ação/FII)
  - Campo para ticker
  - Campo para quantidade
  - Campo para preço
  - Seleção de tipo (COMPRA/VENDA)
  - Campo para data (dd/mm/yyyy)
  - Campo para carteira_id

#### Editar Transação
- Mesmos campos do formulário de adição
- Pré-preenchido com dados da transação

#### Deletar Transação
- Confirmação antes de deletar
- Feedback visual após deleção

### 3. Design

#### Cores
- Verde para valores positivos
- Vermelho para valores negativos
- Azul para ações
- Laranja para FIIs
- Fundo claro para melhor legibilidade

#### Layout
- Responsivo (desktop e mobile)
- Menu lateral para navegação
- Cabeçalho com informações gerais
- Área principal com conteúdo
- Rodapé com informações adicionais

#### Componentes
- Tabelas com ordenação
- Gráficos interativos
- Formulários com validação
- Modais para confirmações
- Tooltips para informações adicionais

### 4. Integração com API

#### Endpoints Utilizados
- GET /transacoes/acoes/listar
- GET /transacoes/fii/listar
- POST /transacoes/acoes/adicionar
- POST /transacoes/fii/adicionar
- PUT /transacoes/acoes/atualizar/{id}
- PUT /transacoes/fii/atualizar/{id}
- DELETE /transacoes/acoes/deletar/{id}
- DELETE /transacoes/fii/deletar/{id}
- GET /carteira/acoes
- GET /carteira/fii

#### Tratamento de Erros
- Exibir mensagens de erro amigáveis
- Feedback visual para operações
- Validação de formulários
- Tratamento de timeout
- Retry em caso de falha

### 5. Performance

- Lazy loading de dados
- Paginação de listas
- Cache de dados frequentes
- Otimização de imagens
- Compressão de assets

### 6. Segurança

- Validação de inputs
- Sanitização de dados
- Proteção contra XSS
- HTTPS obrigatório
- Rate limiting

## Como Usar Este Prompt

1. Ao iniciar o desenvolvimento, abra este arquivo
2. Siga as seções em ordem
3. Use como checklist para implementação
4. Atualize conforme necessário

## Próximos Passos

1. Configurar ambiente de desenvolvimento
2. Criar estrutura base do projeto
3. Implementar autenticação
4. Desenvolver componentes base
5. Integrar com API
6. Implementar funcionalidades
7. Testar e otimizar
8. Deploy

## Observações

- Manter consistência com a API
- Seguir padrões de UI/UX
- Documentar decisões importantes
- Manter código organizado
- Fazer commits frequentes
- Testar em diferentes dispositivos 