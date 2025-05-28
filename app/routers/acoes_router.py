from fastapi import APIRouter, HTTPException, Query

from app.services.acoes import Acao
from app.services.indice_refresher import IndiceRefresher
from app.services import score_acao

router = APIRouter(prefix="/acoes", tags=["Ações"])

refresher = IndiceRefresher()


@router.get("/detalhado", summary="Retorna informações detalhadas da ação")
def obter_detalhes_acao(ticker: str = Query(..., description="Ticker da ação, ex: ITSA4")):
    try:
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        acao = Acao(ticker)
        indices = refresher.get_indices()
        indice_base = refresher.melhor_indice()

        dy_estimado = (acao.dy_estimado * 100) if acao.dy_estimado else 0
        teto_dy_valor = (acao.dy_estimado * acao.cotacao) / (indice_base / 100) if acao.dy_estimado else 0
        real = dy_estimado - indices['ipca_atual']
        base = acao.calcular_teto_cotacao_lucro() or teto_dy_valor
        potencial = round(((base - acao.cotacao) / acao.cotacao) * 100, 2)
        nota_risco = 11 - acao.risco_geral
        score_valor = score_acao.evaluate_company(acao.acao, indice_base)
        cota_necessaria = round(1000 / ((acao.dy_estimado * acao.cotacao) / 12), 0) if acao.dy_estimado else 0
        investimento_necessario = cota_necessaria * acao.cotacao
        

        return {
            "ticker": ticker.replace(".SA", ""),
            "cotacao": round(acao.cotacao, 2),
            "lucro_liquido": acao.lucro_liquido,
            "valor_mercado": acao.valor_mercado,
            "vpa": acao.vpa,
            "lpa": acao.lpa,
            "roe": round(acao.roe, 2) if acao.roe else None,
            "dy_estimado": round(dy_estimado, 2),
            "valor_teto_por_dy": round(teto_dy_valor, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "earning_yield": round(acao.earning_yield, 2),
            "nota_risco": round(nota_risco, 2),
            "score": round(score_valor, 2),
            "margem_liquida": acao.margem_liquida,
            "liquidez_corrente": acao.liquidez_corrente,
            "divida_ebitda": acao.div_ebitda,
            "receita": acao.receita,
            "lucro": acao.lucro,
            "free_float": acao.free_float,
            "pl": acao.pl,
            "teto_por_lucro": round(acao.calcular_teto_cotacao_lucro(), 2) if acao.calcular_teto_cotacao_lucro() else None,
            "cotas_necessarias_para_1000_mensais": cota_necessaria,
            "investimento_necessario_para_1000_mensais": round(investimento_necessario, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar", summary="Retorna informações resumidas da ação para radar")
def obter_dados_acao(ticker: str = Query(..., description="Ticker da ação, ex: ITSA4")):
    try:
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        acao = Acao(ticker)
        indices = refresher.get_indices()
        indice_base = refresher.melhor_indice()

        dy_estimado = (acao.dy_estimado * 100) if acao.dy_estimado else 0
        teto_dy_valor = (acao.dy_estimado * acao.cotacao) / (indice_base / 100) if acao.dy_estimado else 0
        real = dy_estimado - indices['ipca_atual']
        base = acao.calcular_teto_cotacao_lucro() or teto_dy_valor
        potencial = round(((base - acao.cotacao) / acao.cotacao) * 100, 2)
        nota_risco = 11 - acao.risco_geral
        score_valor = score_acao.evaluate_company(acao.acao, indice_base)
        criteria_sum = (sum([
            (acao.calcular_teto_cotacao_lucro() or 0) > acao.cotacao,
            teto_dy_valor > acao.cotacao,
            dy_estimado >= indice_base,
            dy_estimado >= (indices['selic_atual'] - indices['ipca_atual']),
            real > 0,
            potencial > 0,
            acao.earning_yield > (indices['selic_atual'] - indices['ipca_atual']),
        ])) if (acao.calcular_teto_cotacao_lucro() or 0) > acao.cotacao else 0
        comprar = (
            criteria_sum == 7 or
            (acao.calcular_teto_cotacao_lucro() or 0) > acao.cotacao or
            (teto_dy_valor > acao.cotacao and dy_estimado >= (indices['selic_atual'] - indices['ipca_atual']))
        )

        return {
            "ticker": ticker.replace(".SA", ""),
            "cotacao": round(acao.cotacao, 2),
            "teto_por_lucro": round(acao.calcular_teto_cotacao_lucro(), 2) if acao.calcular_teto_cotacao_lucro() else None,
            "dy_estimado": round(dy_estimado, 2),
            "valor_teto_por_dy": round(teto_dy_valor, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "earning_yield": round(acao.earning_yield, 2),
            "nota_risco": round(nota_risco, 2),
            "score": round(score_valor, 2),
            "criteria_sum": int(criteria_sum),
            "comprar": bool(comprar),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
