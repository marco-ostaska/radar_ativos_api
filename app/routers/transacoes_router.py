from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import sqlite3
import os

router = APIRouter(
    prefix="/transacoes",
    tags=["Transações"]
)

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