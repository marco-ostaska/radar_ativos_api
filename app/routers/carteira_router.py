from fastapi import APIRouter, HTTPException, Query
from app.services.acoes import Acao
import sqlite3
import os

router = APIRouter(
    prefix="/carteira",
    tags=["Carteira"]
)

@router.get("/acoes")
async def obter_carteira_acoes(
    carteira_id: int = Query(..., description="ID da carteira")
):
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Busca todas as ações únicas da carteira e suas quantidades
        cursor.execute("""
            SELECT ticker, 
                   SUM(CASE WHEN tipo_transacao = 'COMPRA' THEN quantidade 
                           WHEN tipo_transacao = 'VENDA' THEN -quantidade 
                           ELSE 0 END) as quantidade
            FROM transacoes_acoes
            WHERE carteira_id = ?
            GROUP BY ticker
            HAVING quantidade > 0
        """, (carteira_id,))
        
        acoes = cursor.fetchall()
        if not acoes:
            return []
        
        resultado = []
        for ticker, quantidade in acoes:
            # Busca todas as transações da ação
            cursor.execute("""
                SELECT tipo_transacao, preco, quantidade
                FROM transacoes_acoes
                WHERE ticker = ? AND carteira_id = ?
                ORDER BY data_transacao
            """, (ticker, carteira_id))
            
            transacoes = cursor.fetchall()
            
            # Calcula preço médio
            preco_medio = 0
            quantidade_total = 0
            for tipo, preco, qtd in transacoes:
                if tipo == 'COMPRA':
                    preco_medio = ((preco_medio * quantidade_total) + (preco * qtd)) / (quantidade_total + qtd)
                    quantidade_total += qtd
                elif tipo == 'VENDA':
                    quantidade_total -= qtd
            
            # Obtém preço atual
            acao = Acao(ticker)
            preco_atual = acao.cotacao
            
            # Calcula variação
            variacao = ((preco_atual - preco_medio) / preco_medio) * 100 if preco_medio > 0 else 0
            
            # Calcula valor investido e saldo
            valor_investido = preco_medio * quantidade
            saldo = preco_atual * quantidade
            
            resultado.append({
                "ticker": ticker,
                "quantidade": quantidade,
                "preco_medio": round(preco_medio, 2),
                "preco_atual": round(preco_atual, 2),
                "variacao": round(variacao, 2),
                "valor_investido": round(valor_investido, 2),
                "saldo": round(saldo, 2)
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter carteira: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close() 