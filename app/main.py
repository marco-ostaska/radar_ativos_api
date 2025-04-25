from app.services.acoes import Acao
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

@app.get("/acoes/detalhado")
def obter_detalhes_acao(ticker: str = Query(..., description="Ticker da ação, ex: ITSA4")):
    """
    Retorna informações detalhadas de uma ação, incluindo potencial de valorização e análise de risco.
    """
    try:
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        acao_obj = Acao(ticker)
        indice_base = melhor_indice()
        indices = get_indices()

        dy_estimado = (acao_obj.dy_estimado * 100) if acao_obj.dy_estimado else 0
        teto_dy_valor = (acao_obj.dy_estimado * acao_obj.cotacao) / (indice_base / 100) if acao_obj.dy_estimado else 0
        teto_por_lucro = acao_obj.calcular_teto_cotacao_lucro()
        real = dy_estimado - indices['ipca_atual']
        base = teto_por_lucro if teto_por_lucro else teto_dy_valor
        potencial = round(((base - acao_obj.cotacao) / acao_obj.cotacao) * 100, 2)
        nota_risco = 11 - acao_obj.risco_geral
        score_valor = score.evaluate_company(acao_obj.acao, indice_base)
        cota_necessaria = round(1000 / ((acao_obj.dy_estimado * acao_obj.cotacao) / 12), 0) if acao_obj.dy_estimado else 0
        investimento_necessario = cota_necessaria * acao_obj.cotacao

        return {
            "ticker": ticker.replace(".SA", ""),
            "cotacao": round(acao_obj.cotacao, 2),
            "lucro_liquido": acao_obj.lucro_liquido,
            "valor_mercado": acao_obj.valor_mercado,
            "vpa": acao_obj.vpa,
            "lpa": acao_obj.lpa,
            "roe": round(acao_obj.roe, 2) if acao_obj.roe else None,
            "dy_estimado": round(dy_estimado, 2),
            "valor_teto_por_dy": round(teto_dy_valor, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "earning_yield": round(acao_obj.earning_yield, 2),
            "nota_risco": round(nota_risco, 2),
            "score": round(score_valor, 2),
            "margem_liquida": acao_obj.margem_liquida,
            "liquidez_corrente": acao_obj.liquidez_corrente,
            "divida_ebitda": acao_obj.div_ebitda,
            "receita": acao_obj.receita,
            "lucro": acao_obj.lucro,
            "free_float": acao_obj.free_float,
            "pl": acao_obj.pl,
            "teto_por_lucro": round(teto_por_lucro, 2) if teto_por_lucro else None,
            "cotas_necessarias_para_1000_mensais": cota_necessaria,
            "investimento_necessario_para_1000_mensais": round(investimento_necessario, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/acoes/radar")
def obter_dados_acao(ticker: str = Query(..., description="Ticker da ação, ex: ITSA4")):
    """
    Retorna informações resumidas da ação para radar de oportunidades.
    """
    try:
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        indice_base = melhor_indice()
        indices = get_indices()

        acao_obj = Acao(ticker)

        dy_estimado = (acao_obj.dy_estimado * 100) if acao_obj.dy_estimado else 0
        teto_dy_valor = (acao_obj.dy_estimado * acao_obj.cotacao) / (indice_base / 100) if acao_obj.dy_estimado else 0
        teto_por_lucro = acao_obj.calcular_teto_cotacao_lucro()
        real = dy_estimado - indices['ipca_atual']
        base = teto_por_lucro if teto_por_lucro else teto_dy_valor
        potencial = round(((base - acao_obj.cotacao) / acao_obj.cotacao) * 100, 2)
        nota_risco = 11 - acao_obj.risco_geral
        score_valor = score.evaluate_company(acao_obj.acao, indice_base)

        return {
            "ticker": ticker.replace(".SA", ""),
            "cotacao": round(acao_obj.cotacao, 2),
            "teto_por_lucro": round(teto_por_lucro, 2) if teto_por_lucro else None,
            "dy_estimado": round(dy_estimado, 2),
            "valor_teto_por_dy": round(teto_dy_valor, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "earning_yield": round(acao_obj.earning_yield, 2),
            "nota_risco": round(nota_risco, 2),
            "score": round(score_valor, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
