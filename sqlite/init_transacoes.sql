-- Tabela para transações de ações
CREATE TABLE IF NOT EXISTS transacoes_acoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('COMPRA', 'VENDA', 'DESDOBRO', 'AGRUPAMENTO')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    carteira_id INTEGER NOT NULL,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_ticker ON transacoes_acoes(ticker);
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_data ON transacoes_acoes(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_carteira ON transacoes_acoes(carteira_id);

-- Trigger para atualizar data_atualizacao
CREATE TRIGGER IF NOT EXISTS update_transacoes_acoes_timestamp 
AFTER UPDATE ON transacoes_acoes
BEGIN
    UPDATE transacoes_acoes SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END; 