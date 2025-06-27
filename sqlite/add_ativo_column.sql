-- Adiciona campo ativo na tabela transacoes_acoes
ALTER TABLE transacoes_acoes ADD COLUMN ativo BOOLEAN DEFAULT 1;

-- Adiciona campo ativo na tabela transacoes_fii
ALTER TABLE transacoes_fii ADD COLUMN ativo BOOLEAN DEFAULT 1; 