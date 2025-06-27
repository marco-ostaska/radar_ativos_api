-- Criação consolidada do banco Radar Ativos

-- Tipos de ativos
CREATE TABLE IF NOT EXISTS tipos (
    tipo TEXT PRIMARY KEY,
    spread INTEGER,
    risco_operacional INTEGER
);

-- Ativos (tickers)
CREATE TABLE IF NOT EXISTS ativos (
    ticker TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    FOREIGN KEY (tipo) REFERENCES tipos(tipo)
);

-- Índices econômicos
CREATE TABLE IF NOT EXISTS indices_banco_central (
    indice TEXT PRIMARY KEY,
    valor REAL,
    data_atualizacao TEXT
);

-- Transações de ações
CREATE TABLE IF NOT EXISTS transacoes_acoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('compra', 'venda', 'desdobramento', 'agrupamento', 'bonificacao')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    carteira_id INTEGER,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Transações de FIIs
CREATE TABLE IF NOT EXISTS transacoes_fii (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('compra', 'venda', 'desdobramento', 'agrupamento', 'bonificacao')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    carteira_id INTEGER,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Carteira de ações
CREATE TABLE IF NOT EXISTS carteira_acoes (
    ticker TEXT PRIMARY KEY,
    quantidade_total INTEGER NOT NULL DEFAULT 0,
    preco_medio REAL NOT NULL DEFAULT 0,
    total_investido REAL NOT NULL DEFAULT 0,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Carteira de FIIs
CREATE TABLE IF NOT EXISTS carteira_fiis (
    ticker TEXT PRIMARY KEY,
    quantidade_total INTEGER NOT NULL DEFAULT 0,
    preco_medio REAL NOT NULL DEFAULT 0,
    total_investido REAL NOT NULL DEFAULT 0,
    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES ativos(ticker)
);

-- Notas de ações por carteira
CREATE TABLE IF NOT EXISTS notas_acoes (
    carteira_id INTEGER NOT NULL,
    ticker TEXT NOT NULL,
    nota INTEGER NOT NULL CHECK(nota >= 0 AND nota <= 100),
    PRIMARY KEY (carteira_id, ticker)
);

-- Notas de FIIs por carteira
CREATE TABLE IF NOT EXISTS notas_fiis (
    carteira_id INTEGER NOT NULL,
    ticker TEXT NOT NULL,
    nota INTEGER NOT NULL CHECK(nota >= 0 AND nota <= 100),
    PRIMARY KEY (carteira_id, ticker)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_ticker ON transacoes_acoes(ticker);
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_data ON transacoes_acoes(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_acoes_carteira ON transacoes_acoes(carteira_id);

CREATE INDEX IF NOT EXISTS idx_transacoes_fii_ticker ON transacoes_fii(ticker);
CREATE INDEX IF NOT EXISTS idx_transacoes_fii_data ON transacoes_fii(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_fii_carteira ON transacoes_fii(carteira_id);

-- Triggers para atualizar data_atualizacao
CREATE TRIGGER IF NOT EXISTS update_transacoes_acoes_timestamp 
AFTER UPDATE ON transacoes_acoes
BEGIN
    UPDATE transacoes_acoes SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_transacoes_fii_timestamp 
AFTER UPDATE ON transacoes_fii
BEGIN
    UPDATE transacoes_fii SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
