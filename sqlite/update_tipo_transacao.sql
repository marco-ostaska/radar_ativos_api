-- Remove a constraint antiga
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- Cria uma tabela temporária com a nova estrutura
CREATE TABLE transacoes_acoes_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK(tipo_transacao IN ('COMPRA', 'VENDA', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    carteira_id INTEGER NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (carteira_id) REFERENCES carteiras (id)
);

-- Copia os dados da tabela antiga para a nova, definindo ativo como 1
INSERT INTO transacoes_acoes_temp (id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo)
SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, 1
FROM transacoes_acoes;

-- Remove a tabela antiga
DROP TABLE transacoes_acoes;

-- Renomeia a tabela temporária
ALTER TABLE transacoes_acoes_temp RENAME TO transacoes_acoes;

-- Faz o mesmo para a tabela de FIIs
CREATE TABLE transacoes_fii_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_transacao TEXT NOT NULL,
    tipo_transacao TEXT NOT NULL CHECK(tipo_transacao IN ('COMPRA', 'VENDA', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO')),
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    carteira_id INTEGER NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (carteira_id) REFERENCES carteiras (id)
);

INSERT INTO transacoes_fii_temp (id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo)
SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, 1
FROM transacoes_fii;

DROP TABLE transacoes_fii;

ALTER TABLE transacoes_fii_temp RENAME TO transacoes_fii;

COMMIT;
PRAGMA foreign_keys=ON; 