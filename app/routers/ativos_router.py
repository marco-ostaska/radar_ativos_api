from fastapi import APIRouter, HTTPException, Query
import sqlite3
import logging
from typing import Dict, Any
from app.utils.redis_cache import redis_client

router = APIRouter(prefix="/ativos", tags=["Ativos"])

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validar_formato_ticker(ticker: str) -> tuple[str, str]:
    """
    Valida e normaliza o formato do ticker.
    Retorna (ticker_sem_sa, ticker_com_sa)
    """
    ticker = ticker.upper().strip()
    ticker_sem_sa = ticker.replace('.SA', '')
    ticker_com_sa = ticker_sem_sa + '.SA'
    
    # Validação básica do formato
    if len(ticker_sem_sa) < 4:
        raise HTTPException(status_code=400, detail="Ticker deve ter pelo menos 4 caracteres")
    
    return ticker_sem_sa, ticker_com_sa

def ticker_existe_no_banco(ticker_sem_sa: str, conn: sqlite3.Connection) -> bool:
    """Verifica se o ticker existe na tabela ativos (sem .SA)."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ativos WHERE ticker = ?", (ticker_sem_sa,))
    return cursor.fetchone()[0] > 0

def invalidar_cache_ticker(ticker_sem_sa: str, ticker_com_sa: str) -> None:
    """
    Remove todas as entradas de cache relacionadas ao ticker antigo.
    """
    # Padrões de chaves do cache que precisam ser removidas
    cache_patterns = [
        f"acao:{ticker_com_sa}",
        f"fii_yf:{ticker_com_sa}",
        f"fiiscom:{ticker_sem_sa}",
        f"investidor10:{ticker_sem_sa}"
    ]
    
    for pattern in cache_patterns:
        try:
            redis_client.delete(pattern)
            logger.info(f"Cache removido: {pattern}")
        except Exception as e:
            logger.warning(f"Erro ao remover cache {pattern}: {e}")

@router.put("/rename", summary="Renomeia um ticker em todo o banco de dados")
def renomear_ativo(
    ticker_antigo: str = Query(..., description="Ticker atual a ser renomeado (ex: PETR4)"),
    ticker_novo: str = Query(..., description="Novo ticker (ex: PETR3)")
):
    """
    Renomeia um ticker em todas as tabelas do banco de dados.
    
    Esta operação é atômica - ou todas as tabelas são atualizadas ou nenhuma.
    Também remove as entradas relacionadas do cache Redis.
    
    Tabelas atualizadas:
    - ativos (sem .SA)
    - transacoes_acoes (com .SA)
    - transacoes_fii (com .SA)
    - notas_acoes (com .SA)
    - notas_fiis (com .SA)
    """
    
    # Validar e normalizar tickers
    try:
        ticker_antigo_sem_sa, ticker_antigo_com_sa = validar_formato_ticker(ticker_antigo)
        ticker_novo_sem_sa, ticker_novo_com_sa = validar_formato_ticker(ticker_novo)
    except HTTPException as e:
        raise e
    
    if ticker_antigo_sem_sa == ticker_novo_sem_sa:
        raise HTTPException(status_code=400, detail="Ticker antigo e novo não podem ser iguais")
    
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        
        # Verificar se ticker antigo existe (sem .SA na tabela ativos)
        if not ticker_existe_no_banco(ticker_antigo_sem_sa, conn):
            raise HTTPException(
                status_code=404,
                detail=f"Ticker {ticker_antigo_sem_sa} não encontrado no banco de dados"
            )
        
        # Verificar se ticker novo já existe (sem .SA na tabela ativos)
        if ticker_existe_no_banco(ticker_novo_sem_sa, conn):
            raise HTTPException(
                status_code=409,
                detail=f"Ticker {ticker_novo_sem_sa} já existe no banco de dados"
            )
        
        # Iniciar transação
        conn.execute("BEGIN TRANSACTION")
        
        # Contar registros que serão afetados para logging
        tabelas_info = {}
        
        # Para tabela ativos (sem .SA)
        cursor.execute("SELECT COUNT(*) FROM ativos WHERE ticker = ?", (ticker_antigo_sem_sa,))
        tabelas_info["ativos"] = cursor.fetchone()[0]
        
        # Para outras tabelas (com .SA)
        queries_count_com_sa = [
            ("transacoes_acoes", "SELECT COUNT(*) FROM transacoes_acoes WHERE ticker = ?"),
            ("transacoes_fii", "SELECT COUNT(*) FROM transacoes_fii WHERE ticker = ?"),
            ("notas_acoes", "SELECT COUNT(*) FROM notas_acoes WHERE ticker = ?"),
            ("notas_fiis", "SELECT COUNT(*) FROM notas_fiis WHERE ticker = ?")
        ]
        
        for tabela, query in queries_count_com_sa:
            cursor.execute(query, (ticker_antigo_com_sa,))
            count = cursor.fetchone()[0]
            tabelas_info[tabela] = count
        
        # Executar updates em todas as tabelas
        total_registros_atualizados = 0
        
        # Update na tabela ativos (sem .SA)
        cursor.execute("UPDATE ativos SET ticker = ? WHERE ticker = ?",
                      (ticker_novo_sem_sa, ticker_antigo_sem_sa))
        total_registros_atualizados += cursor.rowcount
        
        # Updates nas outras tabelas (com .SA)
        queries_update_com_sa = [
            "UPDATE transacoes_acoes SET ticker = ? WHERE ticker = ?",
            "UPDATE transacoes_fii SET ticker = ? WHERE ticker = ?",
            "UPDATE notas_acoes SET ticker = ? WHERE ticker = ?",
            "UPDATE notas_fiis SET ticker = ? WHERE ticker = ?"
        ]
        
        for query in queries_update_com_sa:
            cursor.execute(query, (ticker_novo_com_sa, ticker_antigo_com_sa))
            total_registros_atualizados += cursor.rowcount
        
        # Commit da transação
        conn.commit()
        
        # Invalidar cache Redis após sucesso da transação
        invalidar_cache_ticker(ticker_antigo_sem_sa, ticker_antigo_com_sa)
        
        # Log da operação
        logger.info(f"Rename realizado: {ticker_antigo_sem_sa} -> {ticker_novo_sem_sa}")
        logger.info(f"Registros atualizados por tabela: {tabelas_info}")
        logger.info(f"Total de registros atualizados: {total_registros_atualizados}")
        
        return {
            "mensagem": f"Ticker {ticker_antigo_sem_sa} renomeado para {ticker_novo_sem_sa} com sucesso",
            "ticker_antigo": ticker_antigo_sem_sa,
            "ticker_novo": ticker_novo_sem_sa,
            "ticker_antigo_com_sa": ticker_antigo_com_sa,
            "ticker_novo_com_sa": ticker_novo_com_sa,
            "registros_atualizados_por_tabela": tabelas_info,
            "total_registros_atualizados": total_registros_atualizados,
            "cache_invalidado": True
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (já tratadas)
        conn.rollback()
        raise
        
    except Exception as e:
        # Rollback em caso de erro inesperado
        conn.rollback()
        logger.error(f"Erro durante rename {ticker_antigo} -> {ticker_novo}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno durante operação de rename: {str(e)}"
        )
        
    finally:
        conn.close()

@router.get("/verificar/{ticker}", summary="Verifica se um ticker existe no banco")
def verificar_ticker(ticker: str):
    """
    Verifica se um ticker existe no banco de dados e retorna informações básicas.
    """
    try:
        ticker_sem_sa, ticker_com_sa = validar_formato_ticker(ticker)
    except HTTPException as e:
        raise e
    
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        
        # Buscar informações do ticker na tabela ativos (sem .SA)
        cursor.execute("SELECT ticker, tipo FROM ativos WHERE ticker = ?", (ticker_sem_sa,))
        result = cursor.fetchone()
        
        if not result:
            return {
                "ticker": ticker_sem_sa,
                "ticker_com_sa": ticker_com_sa,
                "existe": False,
                "tipo": None,
                "tabelas_com_registros": {}
            }
        
        ticker_db, tipo = result
        
        # Contar registros em cada tabela (com .SA para outras tabelas)
        tabelas_info = {}
        queries_count = [
            ("transacoes_acoes", "SELECT COUNT(*) FROM transacoes_acoes WHERE ticker = ?"),
            ("transacoes_fii", "SELECT COUNT(*) FROM transacoes_fii WHERE ticker = ?"),
            ("notas_acoes", "SELECT COUNT(*) FROM notas_acoes WHERE ticker = ?"),
            ("notas_fiis", "SELECT COUNT(*) FROM notas_fiis WHERE ticker = ?")
        ]
        
        for tabela, query in queries_count:
            cursor.execute(query, (ticker_com_sa,))
            count = cursor.fetchone()[0]
            if count > 0:
                tabelas_info[tabela] = count
        
        return {
            "ticker": ticker_db,
            "ticker_com_sa": ticker_com_sa,
            "existe": True,
            "tipo": tipo,
            "tabelas_com_registros": tabelas_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar ticker: {str(e)}")
        
    finally:
        conn.close()