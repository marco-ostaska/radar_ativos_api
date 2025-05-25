-- Tabela para tipos de ativos, com spread e risco
CREATE TABLE IF NOT EXISTS tipos (
    tipo TEXT PRIMARY KEY,
    spread INTEGER,
    risco_operacional INTEGER
);

-- Tabela para ativos (tickers) referenciando tipos
CREATE TABLE IF NOT EXISTS ativos (
    ticker TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    FOREIGN KEY (tipo) REFERENCES tipos(tipo)
);

CREATE TABLE indices_banco_central (
    indice TEXT PRIMARY KEY,   -- Ex: 'selic', 'ipca', 'ipca_atual', etc
    valor REAL,                -- Valor correspondente ao índice
    data_atualizacao TEXT      -- Data/hora da última atualização (opcional)
);