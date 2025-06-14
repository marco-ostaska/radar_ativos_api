from app.db.indicadores_ativos_db import IndicadoresAtivosDB
from app.services.banco_central import SELIC, IPCA
from app.services.indice_refresher import IndiceRefresher
from app.services.fii import FII
from app.services import score_fii


class FiiDetalhe:
    """
    Serviço para analisar e calcular detalhes de um FII.
    """

    def __init__(self):
        self.indices_service = IndiceRefresher()
        self.db = IndicadoresAtivosDB()

    def get_radar(self, ticker: str) -> dict:
        """
        Retorna os dados simplificados do FII para tela de radar.

        :param ticker: Código do FII
        :param tipo: Categoria do FII (ex: 'logistica', 'papel')
        :return: Dicionário com dados de radar
        """
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        ativo = FII(ticker)
        tipo = ativo.i10_service.get_segmento()
        spread = self.db.get_spread(tipo)
        indice_base = self.indices_service.melhor_indice()
        spread_total = spread + indice_base
        indices = self.indices_service.get_indices()

        dy_estimado = (ativo.dividendo_estimado * 100) / ativo.cotacao
        teto_div = ativo.dividendo_estimado / spread_total * 100
        real = dy_estimado - indices["ipca_atual"]
        potencial = round(((teto_div - ativo.cotacao) / ativo.cotacao) * 100, 2)
        risco = round(11 - ativo.overall_risk(risco_operacional(        tipo = ativo.i10_service.get_segmento()
)), 1)
        score = score_fii.evaluate_fii(ativo, indice_base)
        criteria_sum = sum([
                            ativo.vpa > ativo.cotacao,
                            teto_div > ativo.cotacao,
                            real > (indices["selic_atual"] - indices["ipca_atual"]),
                        ])
  
        comprar = int(criteria_sum) == 3

        return {
            "tipo": tipo,
            "spread": round(spread, 4),
            "melhor_indice": indice_base,
            "ticker": ativo.ticker.split(".")[0],
            "cotacao": round(ativo.cotacao, 2),
            "vpa": round(ativo.vpa, 2),
            "teto_div": round(teto_div, 2),
            "dy_estimado": round(dy_estimado, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "nota_risco": risco,
            "score": score,
            "indice_base": indice_base,
            "spread_usado": spread_total,
            "criteria_sum": int(criteria_sum),
            "comprar": bool(comprar),

        }

    def get_detalhado(self, ticker: str) -> dict:
        """
        Retorna todos os dados detalhados do FII.

        :param ticker: Código do FII
        :param tipo: Categoria do FII
        :return: Dicionário com todos os detalhes
        """
        ticker = ticker.upper()
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        ativo = FII(ticker)
        tipo = ativo.i10_service.get_segmento()
        spread = self.db.get_spread(tipo)
        indice_base = self.indices_service.melhor_indice()
        spread_total = spread + indice_base
        indices = self.indices_service.get_indices()

        dy_estimado = (ativo.dividendo_estimado * 100) / ativo.cotacao
        teto_div = ativo.dividendo_estimado / spread_total * 100
        real = dy_estimado - indices["ipca_atual"]
        potencial = round(((teto_div - ativo.cotacao) / ativo.cotacao) * 100, 2)
        risco = round(11 - ativo.overall_risk(risco_operacional(tipo)), 1)
        cotas_necessarias = round(12000 / ativo.dividendo_estimado, 2)
        investimento_necessario = round(cotas_necessarias * ativo.cotacao, 2)

        return {
            "ticker": ativo.ticker.split(".")[0],
            "cotacao": round(ativo.cotacao, 2),
            "valor_patrimonial": round(ativo.valor_patrimonial, 2) if ativo.valor_patrimonial else None,
            "cotas_emitidas": int(ativo.cotas_emitidas) if ativo.cotas_emitidas else None,
            "vpa": round(ativo.vpa, 2),
            "pvp": round(ativo.pvp, 2),
            "dividend_yield": round(ativo.dividend_yield * 100, 2),
            "dividendo_estimado": round(ativo.dividendo_estimado, 2),
            "dy_estimado": round(dy_estimado, 2),
            "teto_div": round(teto_div, 2),
            "rendimento_real": round(real, 2),
            "potencial": potencial,
            "risco_liquidez": ativo.risco_liquidez,
            "risco_tamanho": ativo.risco_tamanho,
            "risco_preco_volatilidade": ativo.risco_preco_volatilidade,
            "risco_rendimento": ativo.risco_rendimento,
            "nota_risco": risco,
            "indice_base": indice_base,
            "spread": round(spread, 4),
            "spread_usado": spread_total,
            "historico_dividendos": {k: round(v, 4) for k, v in ativo.historico_dividendos.items()},
            "raw_dividends": ativo.dividends.tail(12).to_dict(),
            "cotas_necessarias_para_1000_mensais": cotas_necessarias,
            "investimento_necessario_para_1000_mensais": investimento_necessario
        }


def risco_operacional(tipo: str) -> int:
    db = IndicadoresAtivosDB()
    risco = db.get_risco(tipo)  # Novo método que consulta a tabela tipos
    return risco if risco is not None else 10  # Valor padrão se não encontrar


def main():
    fii = FiiDetalhe()

    print("\n--- Teste: RADAR ---")
    radar = fii.get_radar("HSML11")
    print(radar)

    print("\n--- Teste: DETALHADO ---")
    detalhado = fii.get_detalhado("HGLG11")
    print(detalhado)


if __name__ == "__main__":
    main()
