from datetime import datetime
from typing import List, Optional
from app.models.transacao_acao import TransacaoAcao, TransacaoAcaoCriar, TipoTransacao
from app.database import get_db

class TransacaoAcaoService:
    def __init__(self):
        self.db = get_db()

    def criar_transacao(self, transacao: TransacaoAcaoCriar) -> TransacaoAcao:
        """Cria uma nova transação de ação."""
        cursor = self.db.cursor()
        
        # Valida e formata o ticker
        ticker = transacao.validar_ticker()
        
        # Valida o tipo de transação
        tipo_transacao = transacao.validar_tipo_transacao()
        
        # Converte a data para o formato do SQLite
        data_transacao = datetime.strptime(transacao.data_transacao, "%d/%m/%Y").strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT INTO transacoes_acoes (ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, data_atualizacao)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            ticker,
            data_transacao,
            tipo_transacao,
            transacao.preco,
            transacao.quantidade,
            transacao.carteira_id
        ))
        
        self.db.commit()
        transacao_id = cursor.lastrowid
        
        return self.buscar_transacao_por_id(transacao_id)

    def buscar_transacao_por_id(self, transacao_id: int) -> Optional[TransacaoAcao]:
        """Busca uma transação pelo ID."""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, data_atualizacao
            FROM transacoes_acoes
            WHERE id = ?
        """, (transacao_id,))
        
        row = cursor.fetchone()
        if row:
            return TransacaoAcao(
                id=row[0],
                ticker=row[1],
                data_transacao=datetime.strptime(row[2], "%Y-%m-%d").strftime("%d/%m/%Y"),
                tipo_transacao=row[3],
                preco=row[4],
                quantidade=row[5],
                carteira_id=row[6],
                data_atualizacao=row[7]
            )
        return None

    def listar_transacoes(self, ticker: Optional[str] = None) -> List[TransacaoAcao]:
        """Lista todas as transações, opcionalmente filtradas por ticker."""
        cursor = self.db.cursor()
        
        if ticker:
            # Valida e formata o ticker
            if not ticker.endswith('.SA'):
                ticker += '.SA'
            ticker = ticker.upper()
            
            cursor.execute("""
                SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, data_atualizacao
                FROM transacoes_acoes
                WHERE ticker = ?
                ORDER BY data_transacao DESC
            """, (ticker,))
        else:
            cursor.execute("""
                SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, data_atualizacao
                FROM transacoes_acoes
                ORDER BY data_transacao DESC
            """)
        
        transacoes = []
        for row in cursor.fetchall():
            transacoes.append(TransacaoAcao(
                id=row[0],
                ticker=row[1],
                data_transacao=datetime.strptime(row[2], "%Y-%m-%d").strftime("%d/%m/%Y"),
                tipo_transacao=row[3],
                preco=row[4],
                quantidade=row[5],
                carteira_id=row[6],
                data_atualizacao=row[7]
            ))
        
        return transacoes

    def atualizar_transacao(self, transacao_id: int, transacao: TransacaoAcaoCriar) -> Optional[TransacaoAcao]:
        """Atualiza uma transação existente."""
        cursor = self.db.cursor()
        
        # Busca a transação atual
        transacao_atual = self.buscar_transacao_por_id(transacao_id)
        if not transacao_atual:
            return None
        
        # Valida e formata o ticker
        ticker = transacao.validar_ticker()
        
        # Valida o tipo de transação
        tipo_transacao = transacao.validar_tipo_transacao()
        
        # Converte a data para o formato do SQLite
        data_transacao = datetime.strptime(transacao.data_transacao, "%d/%m/%Y").strftime("%Y-%m-%d")
        
        # Executa a atualização
        cursor.execute("""
            UPDATE transacoes_acoes
            SET ticker = ?,
                data_transacao = ?,
                tipo_transacao = ?,
                preco = ?,
                quantidade = ?,
                carteira_id = ?,
                data_atualizacao = datetime('now')
            WHERE id = ?
        """, (
            ticker,
            data_transacao,
            tipo_transacao,
            transacao.preco,
            transacao.quantidade,
            transacao.carteira_id,
            transacao_id
        ))
        
        self.db.commit()
        return self.buscar_transacao_por_id(transacao_id)

    def deletar_transacao(self, transacao_id: int) -> bool:
        """Deleta uma transação."""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM transacoes_acoes WHERE id = ?", (transacao_id,))
        self.db.commit()
        return cursor.rowcount > 0

    def aplicar_desdobramento(self, ticker: str, data_desdobramento: str, proporcao_antes: int, proporcao_depois: int) -> bool:
        """
        Aplica um desdobramento nas transações de uma ação.
        
        Args:
            ticker: Código da ação
            data_desdobramento: Data do desdobramento (dd/mm/yyyy)
            proporcao_antes: Proporção antes do desdobramento (ex: 1)
            proporcao_depois: Proporção depois do desdobramento (ex: 10)
        
        Returns:
            bool: True se o desdobramento foi aplicado com sucesso
        """
        cursor = self.db.cursor()
        
        # Valida e formata o ticker
        if not ticker.endswith('.SA'):
            ticker += '.SA'
        ticker = ticker.upper()
        
        # Converte a data para o formato do SQLite
        data_desdobramento = datetime.strptime(data_desdobramento, "%d/%m/%Y").strftime("%Y-%m-%d")
        
        # Calcula o fator de multiplicação
        fator = proporcao_depois / proporcao_antes
        
        # Atualiza as transações anteriores ao desdobramento
        cursor.execute("""
            UPDATE transacoes_acoes
            SET quantidade = quantidade * ?,
                preco = preco / ?,
                data_atualizacao = datetime('now')
            WHERE ticker = ? AND data_transacao < ?
        """, (fator, fator, ticker, data_desdobramento))
        
        # Atualiza a carteira
        cursor.execute("""
            UPDATE carteira_acoes
            SET quantidade_total = quantidade_total * ?,
                preco_medio = preco_medio / ?,
                data_atualizacao = datetime('now')
            WHERE ticker = ?
        """, (fator, fator, ticker))
        
        self.db.commit()
        return True 