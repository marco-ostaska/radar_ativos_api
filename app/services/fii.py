import pandas as pd
import numpy as np
import yfinance as yf
from app.services.investidor10 import Investidor10Service
from app.utils.redis_cache import get_cached_data
from datetime import datetime
from app.db.indicadores_ativos_db import IndicadoresAtivosDB
from app.services.banco_central import SELIC, IPCA
from app.services.indice_refresher import IndiceRefresher
from app.services import score_fii

class FII:
    def __init__(self, ticker: str, force_update: bool = False):
        self.ticker = ticker.upper()

        def fetch_data():
            ticker_obj = yf.Ticker(self.ticker)
            ticker_base = self.ticker.split(".")[0]
            i10_service = Investidor10Service(ticker_base)
            from app.services.fiiscom import FiisComService
            fiiscom_data = FiisComService(ticker_base).dados
            return {
                "info": ticker_obj.info,
                "balance_sheet": ticker_obj.balance_sheet.to_dict(),
                "dividends": {
                    str(k.date()): float(v)
                    for k, v in ticker_obj.dividends.items()
                },
                "i10_segmento": i10_service.get_segmento(),
                "fiiscom": fiiscom_data
            }

        dados = get_cached_data(f"fii:{self.ticker}", None, fetch_data, force=force_update)
        self._info = dados["info"]
        self._balance_sheet = pd.DataFrame(dados["balance_sheet"])
        self._dividends = pd.Series(dados["dividends"])
        self._i10_service = None
        self._i10_segmento = dados.get("i10_segmento")
        self._fiiscom_data = dados.get("fiiscom")

    @property
    def info(self):
        return self._info

    @property
    def balance_sheet(self):
        return self._balance_sheet

    @property
    def dividends(self):
        return self._dividends

    @property
    def i10_service(self):
        if self._i10_service is None:
            ticker = self.ticker.split(".")[0]
            self._i10_service = Investidor10Service(ticker)
        return self._i10_service

    @property
    def i10_segmento(self):
        return self._i10_segmento

    @property
    def fiiscom(self):
        return self._fiiscom_data

    @property
    def valor_patrimonial(self):
        if 'Total Equity Gross Minority Interest' not in self.balance_sheet.index:
            return None
        return self.balance_sheet.loc['Total Equity Gross Minority Interest'].head(1).values[0]

    @property
    def cotas_emitidas(self):
        if 'Ordinary Shares Number' not in self.balance_sheet.index:
            return None
        valor = self.balance_sheet.loc['Ordinary Shares Number'].head(1).values[0]
        if np.isnan(valor):
            return None
        return valor

    @property
    def vpa(self):
        vpa_i10 = None
        vpa_fiiscom = None
        try:
            vpa_i10 = self.i10_service.get_vpa()
        except Exception:
            pass
        try:
            vpa_fiiscom = self.fiiscom.get("Val. Patrimonial p/Cota")
            if vpa_fiiscom:
                vpa_fiiscom = float(vpa_fiiscom.replace(",", "."))
        except Exception:
            pass

        vpas = [v for v in [vpa_i10, vpa_fiiscom] if v is not None]
        if vpas:
            return min(vpas)
        # Cálculo antigo (Yahoo) mantido apenas para referência:
        # if self.valor_patrimonial is not None and self.cotas_emitidas is not None:
        #     return round(self.valor_patrimonial / self.cotas_emitidas, 2)
        return None

    @property
    def cotacao(self):
        if 'currentPrice' in self.info:
            return self.info['currentPrice']
        return self.info.get('ask', 0)

    @property
    def pvp(self):
        return round(self.cotacao / self.vpa, 2) if self.vpa else None

    @property
    def dividend_yield(self):
        return self.dividends.tail(12).sum() / self.cotacao

    @property
    def historico_dividendos(self):
        return {
            '1 mes': self.dividends.tail(1).sum(),
            '3 meses': self.dividends.tail(3).sum(),
            '6 meses': self.dividends.tail(6).sum(),
            '12 meses': self.dividends.tail(12).sum(),
        }

    @property
    def dividendo_estimado(self):
        tres_meses = self.dividends.tail(3).sum() / 3
        seis_meses = self.dividends.tail(6).sum() / 6
        if tres_meses < seis_meses:
            return tres_meses * 12
        return seis_meses * 12

    @property
    def risco_liquidez(self):
        if "averageVolume" not in self.info:
            return 10
        volume = self.info.get("averageVolume", 0)
        if volume > 50000:
            return 1
        elif volume > 20000:
            return 5
        return 10

    @property
    def risco_tamanho(self):
        if "marketCap" not in self.info:
            return 10
        market_cap = self.info.get("marketCap", 0)
        if market_cap < 500_000_000:
            return 5
        return 1

    @property
    def risco_preco_volatilidade(self):
        if "52WeekChange" not in self.info:
            return 10
        variacao_52w = self.info.get("52WeekChange", 0)
        if variacao_52w < -0.15:
            return 10
        if variacao_52w < -0.05:
            return 5
        return 1

    @property
    def risco_rendimento(self):
        if "dividendYield" not in self.info:
            return 10
        dy = self.info.get("dividendYield", 0)
        if dy > 12:
            return 10
        if dy > 8:
            return 5
        if dy < 7:
            return 5
        return 1

    def overall_risk(self, risco_operacional: int) -> float:
        """
        Calcula o risco geral do FII com pesos definidos para cada fator.
        """
        pesos = {
            "liquidez": 0.2,
            "tamanho_fundo": 0.1,
            "preco_volatilidade": 0.1,
            "rendimento": 0.3,
            "operacional": 0.3,
        }

        overall_risk = (
            (self.risco_liquidez * pesos["liquidez"]) +
            (self.risco_preco_volatilidade * pesos["preco_volatilidade"]) +
            (self.risco_tamanho * pesos["tamanho_fundo"]) +
            (self.risco_rendimento * pesos["rendimento"]) +
            (risco_operacional * pesos["operacional"])
        )

        return round(min(max(overall_risk, 1), 10), 1)
    
    def segmento(self) -> str:
        """
        Retorna o tipo do FII (Fundo de Papel, Fundo de Tijolo, etc).
        """
        i10 = self.i10_service
        return i10.get_segmento()

    @staticmethod
    def risco_operacional(tipo: str) -> int:
        db = IndicadoresAtivosDB()
        risco = db.get_risco(tipo)
        return risco if risco is not None else 10

    def get_radar(self) -> dict:
        indices_service = IndiceRefresher()
        db = IndicadoresAtivosDB()

        ticker = self.ticker
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        ativo = self
        tipo = ativo.i10_service.get_segmento()
        spread = db.get_spread(tipo)
        indice_base = indices_service.melhor_indice()
        spread_total = spread + indice_base
        indices = indices_service.get_indices()

        dy_estimado = (ativo.dividendo_estimado * 100) / ativo.cotacao
        teto_div = ativo.dividendo_estimado / spread_total * 100
        real = dy_estimado - indices["ipca_atual"]
        potencial = round(((teto_div - ativo.cotacao) / ativo.cotacao) * 100, 2)
        risco = round(11 - ativo.overall_risk(FII.risco_operacional(tipo)), 1)
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
            "vpa": round(ativo.vpa, 2) if ativo.vpa else None,
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

    def get_detalhado(self) -> dict:
        indices_service = IndiceRefresher()
        db = IndicadoresAtivosDB()

        ticker = self.ticker
        if not ticker.endswith(".SA"):
            ticker += ".SA"

        ativo = self
        tipo = ativo.i10_service.get_segmento()
        spread = db.get_spread(tipo)
        indice_base = indices_service.melhor_indice()
        spread_total = spread + indice_base
        indices = indices_service.get_indices()

        dy_estimado = (ativo.dividendo_estimado * 100) / ativo.cotacao
        teto_div = ativo.dividendo_estimado / spread_total * 100
        real = dy_estimado - indices["ipca_atual"]
        potencial = round(((teto_div - ativo.cotacao) / ativo.cotacao) * 100, 2)
        risco = round(11 - ativo.overall_risk(FII.risco_operacional(tipo)), 1)
        cotas_necessarias = round(12000 / ativo.dividendo_estimado, 2)
        investimento_necessario = round(cotas_necessarias * ativo.cotacao, 2)

        return {
            "ticker": ativo.ticker.split(".")[0],
            "cotacao": round(ativo.cotacao, 2),
            "valor_patrimonial": round(ativo.valor_patrimonial, 2) if ativo.valor_patrimonial else None,
            "cotas_emitidas": int(ativo.cotas_emitidas) if ativo.cotas_emitidas else None,
            "vpa": round(ativo.vpa, 2) if ativo.vpa else None,
            "pvp": round(ativo.pvp, 2) if ativo.pvp else None,
            "dividend_yield": round(ativo.dividend_yield * 100, 2) if ativo.dividend_yield else None,
            "dividendo_estimado": round(ativo.dividendo_estimado, 2) if ativo.dividendo_estimado else None,
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

def convert_unix_date(unix_date: int) -> str:
    date_time = datetime.fromtimestamp(unix_date)
    return date_time.strftime('%d/%m')

def get_investidor10(ticker: str) -> Investidor10Service:
    ticker = ticker.split(".")[0]
    return Investidor10Service(ticker)

def main():
    fii = FII('VGIA11.SA', force_update=True)
    print("\n--- Teste: RADAR (cache) ---")
    print(fii.get_radar())

    
    print("\n--- Teste: RADAR (forçando refresh) ---")
    print(fii.get_radar())

    fii = FII('VGIA11.SA')

    print("\n--- Teste: DETALHADO ---")
    print(fii.get_detalhado())

if __name__ == "__main__":
    main()
