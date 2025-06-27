#!/bin/bash
sqlite3 sqlite/radar_ativos.db <<EOF
CREATE TABLE IF NOT EXISTS notas_acoes (
    carteira_id INTEGER NOT NULL,
    ticker TEXT NOT NULL,
    nota INTEGER NOT NULL CHECK(nota >= 0 AND nota <= 100),
    PRIMARY KEY (carteira_id, ticker)
);
EOF
