from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import sqlite3
import os

router = APIRouter(
    prefix="/transacoes",
    tags=["Transações"]
)

@router.get("/acoes/listar")
def listar_transacoes_acoes(carteira_id: int = Query(..., description="ID da carteira")):
    """
    Lista todas as transações de ações de uma carteira.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade
            FROM transacoes_acoes
            WHERE carteira_id = ?
            ORDER BY data_transacao DESC
        """, (carteira_id,))
        
        transacoes = []
        for row in cursor.fetchall():
            transacoes.append({
                "id": row[0],
                "ticker": row[1],
                "data": row[2],
                "tipo": row[3],
                "preco": row[4],
                "quantidade": row[5],
                "valor_total": row[4] * row[5]
            })
        
        return transacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/fii/listar")
def listar_transacoes_fii(carteira_id: int = Query(..., description="ID da carteira")):
    """
    Lista todas as transações de FIIs de uma carteira.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade
            FROM transacoes_fii
            WHERE carteira_id = ?
            ORDER BY data_transacao DESC
        """, (carteira_id,))
        
        transacoes = []
        for row in cursor.fetchall():
            transacoes.append({
                "id": row[0],
                "ticker": row[1],
                "data": row[2],
                "tipo": row[3],
                "preco": row[4],
                "quantidade": row[5],
                "valor_total": row[4] * row[5]
            })
        
        return transacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/acoes/adicionar")
async def adicionar_transacao_acao(
    ticker: str = Query(..., description="Código da ação (ex: PETR4)"),
    quantidade: int = Query(..., description="Quantidade de ações"),
    preco: float = Query(..., description="Preço unitário da ação"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    carteira_id: int = Query(..., description="ID da carteira"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    # Validações básicas
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    if preco <= 0:
        raise HTTPException(status_code=400, detail="Preço deve ser maior que zero")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Normaliza o tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data, '%d/%m/%Y')
        data_transacao = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Insere a transação
        cursor.execute("""
            INSERT INTO transacoes_acoes (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, data_transacao, tipo, preco, quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Transação adicionada com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar transação: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/fii/adicionar")
async def adicionar_transacao_fii(
    ticker: str = Query(..., description="Código do FII (ex: HGLG11)"),
    quantidade: int = Query(..., description="Quantidade de cotas"),
    preco: float = Query(..., description="Preço unitário da cota"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    carteira_id: int = Query(..., description="ID da carteira"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    # Validações básicas
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    if preco <= 0:
        raise HTTPException(status_code=400, detail="Preço deve ser maior que zero")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Normaliza o tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data, '%d/%m/%Y')
        data_transacao = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Insere a transação
        cursor.execute("""
            INSERT INTO transacoes_fii (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, data_transacao, tipo, preco, quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Transação adicionada com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar transação: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/acoes/deletar/{transacao_id}")
def deletar_transacao_acao(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Deleta uma transação de ação específica.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transacoes_acoes WHERE id = ? AND carteira_id = ?",
            (transacao_id, carteira_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
            
        return {"mensagem": "Transação deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/fii/deletar/{transacao_id}")
def deletar_transacao_fii(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Deleta uma transação de FII específica.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transacoes_fii WHERE id = ? AND carteira_id = ?",
            (transacao_id, carteira_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
            
        return {"mensagem": "Transação deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.put("/acoes/atualizar/{transacao_id}")
def atualizar_transacao_acao(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira"),
    ticker: str = Query(..., description="Código da ação (ex: PETR4)"),
    quantidade: int = Query(..., gt=0, description="Quantidade de ações"),
    preco: float = Query(..., gt=0, description="Preço unitário da ação"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    """
    Atualiza uma transação de ação existente.
    """
    # Validação da data
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        data_formatada = data_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")

    # Normalização do ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'

    # Normalização do tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")

    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes_acoes 
            SET ticker = ?,
                data_transacao = ?,
                tipo_transacao = ?,
                preco = ?,
                quantidade = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ? AND carteira_id = ?
        """, (ticker, data_formatada, tipo, preco, quantidade, transacao_id, carteira_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
            
        return {"mensagem": "Transação atualizada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.put("/fii/atualizar/{transacao_id}")
def atualizar_transacao_fii(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira"),
    ticker: str = Query(..., description="Código do FII (ex: HGLG11)"),
    quantidade: int = Query(..., gt=0, description="Quantidade de cotas"),
    preco: float = Query(..., gt=0, description="Preço unitário da cota"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    """
    Atualiza uma transação de FII existente.
    """
    # Validação da data
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        data_formatada = data_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")

    # Normalização do ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'

    # Normalização do tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")

    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes_fii 
            SET ticker = ?,
                data_transacao = ?,
                tipo_transacao = ?,
                preco = ?,
                quantidade = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ? AND carteira_id = ?
        """, (ticker, data_formatada, tipo, preco, quantidade, transacao_id, carteira_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
            
        return {"mensagem": "Transação atualizada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close() 