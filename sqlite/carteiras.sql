-- Tabela para transações de ações
CREATE TABLE IF NOT EXISTS transacoes_acoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('compra', 'venda', 'desdobramento', 'agrupamento', 'bonificacao')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Tabela para transações de FIIs
CREATE TABLE IF NOT EXISTS transacoes_fiis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('compra', 'venda', 'desdobramento', 'agrupamento', 'bonificacao')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Tabela para carteira de ações (dados calculados)
CREATE TABLE IF NOT EXISTS carteira_acoes (
    ticker TEXT PRIMARY KEY,
    quantidade_total INTEGER NOT NULL DEFAULT 0,
    preco_medio REAL NOT NULL DEFAULT 0,
    total_investido REAL NOT NULL DEFAULT 0,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Tabela para carteira de FIIs (dados calculados)
CREATE TABLE IF NOT EXISTS carteira_fiis (
    ticker TEXT PRIMARY KEY,
    quantidade_total INTEGER NOT NULL DEFAULT 0,
    preco_medio REAL NOT NULL DEFAULT 0,
    total_investido REAL NOT NULL DEFAULT 0,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Índices para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_ticker ON transacoes_acoes(ticker);
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_data ON transacoes_acoes(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_fiis_ticker ON transacoes_fiis(ticker);
CREATE INDEX IF NOT EXISTS idx_transacoes_fiis_data ON transacoes_fiis(data_transacao);

-- Triggers para atualizar data_atualizacao
CREATE TRIGGER IF NOT EXISTS update_transacoes_acoes_timestamp 
AFTER UPDATE ON transacoes_acoes
BEGIN
    UPDATE transacoes_acoes SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_transacoes_fiis_timestamp 
AFTER UPDATE ON transacoes_fiis
BEGIN
    UPDATE transacoes_fiis SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END; 