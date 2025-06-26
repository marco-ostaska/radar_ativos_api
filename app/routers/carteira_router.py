from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, conint
from app.services.acoes import Acao
from app.services.fii import FII
from app.services.score_fii import evaluate_fii
import sqlite3
import os

router = APIRouter(
    prefix="/carteira",
    tags=["Carteira"]
)

# Removido NotaAcaoRequest pois não é mais necessário

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
                   SUM(CASE 
                           WHEN tipo_transacao = 'COMPRA' THEN quantidade 
                           WHEN tipo_transacao = 'VENDA' THEN -quantidade 
                           WHEN tipo_transacao IN ('DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO') THEN quantidade
                           ELSE 0 
                       END) as quantidade
            FROM transacoes_acoes
            WHERE carteira_id = ? AND ativo = 1
            GROUP BY ticker
            HAVING quantidade > 0
        """, (carteira_id,))
        
        acoes = cursor.fetchall()
        if not acoes:
            return []
        
        resultado = []
        saldos = []
        # Primeiro loop para calcular todos os saldos
        for ticker, quantidade in acoes:
            cursor.execute("""
                SELECT tipo_transacao, preco, quantidade
                FROM transacoes_acoes
                WHERE ticker = ? AND carteira_id = ? AND ativo = 1
                ORDER BY data_transacao
            """, (ticker, carteira_id))
            transacoes = cursor.fetchall()
            preco_medio = 0
            quantidade_total = 0
            for tipo, preco, qtd in transacoes:
                if tipo in ['COMPRA', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO']:
                    preco_medio = ((preco_medio * quantidade_total) + (preco * qtd)) / (quantidade_total + qtd)
                    quantidade_total += qtd
                elif tipo == 'VENDA':
                    quantidade_total -= qtd
            acao = Acao(ticker)
            preco_atual = acao.cotacao
            saldo = preco_atual * quantidade
            saldos.append(saldo)
        saldo_total = sum(saldos)
        # Segundo loop para montar resultado com porcentagem
        for idx, (ticker, quantidade) in enumerate(acoes):
            # Busca todas as transações da ação
            cursor.execute("""
                SELECT tipo_transacao, preco, quantidade
                FROM transacoes_acoes
                WHERE ticker = ? AND carteira_id = ? AND ativo = 1
                ORDER BY data_transacao
            """, (ticker, carteira_id))
            
            transacoes = cursor.fetchall()
            
            # Calcula preço médio
            preco_medio = 0
            quantidade_total = 0
            for tipo, preco, qtd in transacoes:
                if tipo in ['COMPRA', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO']:
                    preco_medio = ((preco_medio * quantidade_total) + (preco * qtd)) / (quantidade_total + qtd)
                    quantidade_total += qtd
                elif tipo == 'VENDA':
                    quantidade_total -= qtd
            
            # Obtém preço atual e tetos
            acao = Acao(ticker)
            preco_atual = acao.cotacao
            teto_por_lucro = acao.calcular_teto_cotacao_lucro()
            teto_por_dy = acao.cotacao / acao.dy if acao.dy > 0 else None
            
            # Calcula variação
            variacao = ((preco_atual - preco_medio) / preco_medio) * 100 if preco_medio > 0 else 0
            
            # Calcula valor investido e saldo
            valor_investido = preco_medio * quantidade
            saldo = preco_atual * quantidade
            
            # Calcula indicadores para recomendação
            lucro_latente = (preco_atual / preco_medio - 1) * 100 if preco_medio > 0 else 0
            
            excesso_pl = (preco_atual / teto_por_lucro - 1) * 100 if teto_por_lucro else 0
            excesso_dy = (preco_atual / teto_por_dy - 1) * 100 if teto_por_dy else 0
            
            # Busca nota na tabela notas_acoes
            cursor.execute(
                "SELECT nota FROM notas_acoes WHERE carteira_id = ? AND ticker = ?",
                (carteira_id, ticker)
            )
            row = cursor.fetchone()
            nota = row[0] if row else None

            # Define recomendação
            if excesso_pl > 20 and excesso_dy > 20 and lucro_latente > 30:
                recomendacao = "VENDER ou realizar parcial"
            elif excesso_pl > 10 or excesso_dy > 10:
                recomendacao = "MANTER com cautela"
            elif excesso_pl < 0 and excesso_dy < 0:
                recomendacao = "COMPRAR ou APORTAR"
            else:
                recomendacao = "MANTER"
            
            porcentagem_carteira = (saldo / saldo_total * 100) if saldo_total > 0 else 0
            resultado.append({
                "ticker": ticker,
                "quantidade": quantidade,
                "preco_medio": round(preco_medio, 2),
                "preco_atual": round(preco_atual, 2),
                "variacao": round(variacao, 2),
                "valor_investido": round(valor_investido, 2),
                "saldo": round(saldo, 2),
                "lucro_latente": round(lucro_latente, 2),
                "excesso_pl": round(excesso_pl, 2),
                "excesso_dy": round(excesso_dy, 2),
                "recomendacao": recomendacao,
                "nota": nota,
                "porcentagem_carteira": round(porcentagem_carteira, 2)
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter carteira: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/acoes/nota")
async def setar_nota_acao(
    carteira_id: int = Query(..., description="ID da carteira"),
    ticker: str = Query(..., description="Ticker da ação"),
    nota: int = Query(..., ge=0, le=100, description="Nota de 0 a 100")
):
    """
    Define ou atualiza a nota de um ativo (ação) para uma carteira.
    """
    try:
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO notas_acoes (carteira_id, ticker, nota)
            VALUES (?, ?, ?)
            ON CONFLICT(carteira_id, ticker) DO UPDATE SET nota=excluded.nota
            """,
            (carteira_id, ticker, nota)
        )
        conn.commit()
        return {"mensagem": f"Nota {nota} registrada para {ticker} na carteira {carteira_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar nota: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/fii")
async def obter_carteira_fii(
    carteira_id: int = Query(..., description="ID da carteira")
):
    print("Obtendo carteira de FII")
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Busca todos os FIIs únicos da carteira e suas quantidades
        cursor.execute("""
            SELECT ticker, 
                   SUM(CASE 
                           WHEN tipo_transacao = 'COMPRA' THEN quantidade 
                           WHEN tipo_transacao = 'VENDA' THEN -quantidade 
                           WHEN tipo_transacao IN ('DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO') THEN quantidade
                           ELSE 0 
                       END) as quantidade
            FROM transacoes_fii
            WHERE carteira_id = ? AND ativo = 1
            GROUP BY ticker
            HAVING quantidade > 0
        """, (carteira_id,))
        
        fiis = cursor.fetchall()
        if not fiis:
            return []
        
        resultado = []
        saldos = []
        # Primeiro loop para calcular todos os saldos
        for ticker, quantidade in fiis:
            cursor.execute("""
                SELECT tipo_transacao, preco, quantidade
                FROM transacoes_fii
                WHERE ticker = ? AND carteira_id = ? AND ativo = 1
                ORDER BY data_transacao
            """, (ticker, carteira_id))
            transacoes = cursor.fetchall()
            preco_medio = 0
            quantidade_total = 0
            for tipo, preco, qtd in transacoes:
                if tipo in ['COMPRA', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO']:
                    preco_medio = ((preco_medio * quantidade_total) + (preco * qtd)) / (quantidade_total + qtd)
                    quantidade_total += qtd
                elif tipo == 'VENDA':
                    quantidade_total -= qtd
            fii = FII(ticker)
            preco_atual = fii.cotacao
            saldo = preco_atual * quantidade
            saldos.append(saldo)
        saldo_total = sum(saldos)
        # Segundo loop para montar resultado com porcentagem
        for idx, (ticker, quantidade) in enumerate(fiis):
            # Busca todas as transações do FII
            cursor.execute("""
                SELECT tipo_transacao, preco, quantidade
                FROM transacoes_fii
                WHERE ticker = ? AND carteira_id = ? AND ativo = 1
                ORDER BY data_transacao
            """, (ticker, carteira_id))
            
            transacoes = cursor.fetchall()
            
            # Calcula preço médio
            preco_medio = 0
            quantidade_total = 0
            for tipo, preco, qtd in transacoes:
                if tipo in ['COMPRA', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'BONIFICACAO']:
                    preco_medio = ((preco_medio * quantidade_total) + (preco * qtd)) / (quantidade_total + qtd)
                    quantidade_total += qtd
                elif tipo == 'VENDA':
                    quantidade_total -= qtd
            
            # Obtém preço atual e informações do FII
            fii = FII(ticker)
            preco_atual = fii.cotacao
            
            # Calcula variação
            variacao = ((preco_atual - preco_medio) / preco_medio) * 100 if preco_medio > 0 else 0
            
            # Calcula valor investido e saldo
            valor_investido = preco_medio * quantidade
            saldo = preco_atual * quantidade
            
            # calcula dividendo estimado por cota

            dy_estimado = (fii.dividendo_estimado /12) / fii.cotacao * 100
            dividendo_real = ((dy_estimado/12) *fii.cotacao) / 100
            
            # Calcula rendimento mensal estimado
            rendimento_mensal = (dividendo_real * quantidade)
            
            # Busca nota na tabela notas_fiis
            cursor.execute(
                "SELECT nota FROM notas_fiis WHERE carteira_id = ? AND ticker = ?",
                (carteira_id, ticker)
            )
            row = cursor.fetchone()
            nota = row[0] if row else None

            # Score e recomendação baseada em evaluate_fii
            score = evaluate_fii(fii, 7)
            if fii.pvp >= 1:
                if score <= 4:
                    recomendacao = "VENDER ou realizar parcial"
                else:
                    recomendacao = "MANTER com cautela"
            else:
                if score >= 7.5:
                    recomendacao = "COMPRAR ou APORTAR"
                elif score <= 4:
                    recomendacao = "VENDER ou realizar parcial"
                else:
                    recomendacao = "MANTER"

            porcentagem_carteira = (saldo / saldo_total * 100) if saldo_total > 0 else 0
            resultado.append({
                "ticker": ticker,
                "score": score,
                "quantidade": quantidade,
                "preco_medio": round(preco_medio, 2),
                "preco_atual": round(preco_atual, 2),
                "variacao": round(variacao, 2),
                "valor_investido": round(valor_investido, 2),
                "saldo": round(saldo, 2),
                "dividendo_mensal": round(dividendo_real, 2),
                "rendimento_mensal_estimado": round(rendimento_mensal, 2),
                "dividendo_estimado": round(dy_estimado, 2),
                "dy": round(fii.dividend_yield, 2),
                "pvp": round(fii.pvp, 2),
                "recomendacao": recomendacao,
                "nota": nota,
                "porcentagem_carteira": round(porcentagem_carteira, 2)
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter carteira: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/fii/nota")
async def setar_nota_fii(
    carteira_id: int = Query(..., description="ID da carteira"),
    ticker: str = Query(..., description="Ticker do FII"),
    nota: int = Query(..., ge=0, le=100, description="Nota de 0 a 100")
):
    """
    Define ou atualiza a nota de um FII para uma carteira.
    """
    try:
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO notas_fiis (carteira_id, ticker, nota)
            VALUES (?, ?, ?)
            ON CONFLICT(carteira_id, ticker) DO UPDATE SET nota=excluded.nota
            """,
            (carteira_id, ticker, nota)
        )
        conn.commit()
        return {"mensagem": f"Nota {nota} registrada para {ticker} na carteira {carteira_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar nota: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/acoes/delete")
async def deletar_carteira_acoes(
    carteira_id: int = Query(..., description="ID da carteira de ações a ser deletada")
):
    """
    Deleta todas as transações de uma carteira de ações.
    """
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Verifica se existem transações para esta carteira
        cursor.execute("SELECT COUNT(*) FROM transacoes_acoes WHERE carteira_id = ?", (carteira_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            raise HTTPException(status_code=404, detail=f"Não existem transações para a carteira de ações {carteira_id}")
        
        # Deleta todas as transações associadas à carteira
        cursor.execute("DELETE FROM transacoes_acoes WHERE carteira_id = ?", (carteira_id,))
        
        conn.commit()
        return {"mensagem": f"{count} transações da carteira de ações {carteira_id} foram deletadas com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar carteira: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/fii/delete")
async def deletar_carteira_fii(
    carteira_id: int = Query(..., description="ID da carteira de FII a ser deletada")
):
    """
    Deleta todas as transações de uma carteira de FII.
    """
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Verifica se existem transações para esta carteira
        cursor.execute("SELECT COUNT(*) FROM transacoes_fii WHERE carteira_id = ?", (carteira_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            raise HTTPException(status_code=404, detail=f"Não existem transações para a carteira de FII {carteira_id}")
        
        # Deleta todas as transações associadas à carteira
        cursor.execute("DELETE FROM transacoes_fii WHERE carteira_id = ?", (carteira_id,))
        
        conn.commit()
        return {"mensagem": f"{count} transações da carteira de FII {carteira_id} foram deletadas com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar carteira: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()
