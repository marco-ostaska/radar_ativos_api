import pandas as pd
import numpy as np
import yfinance as yf
from app.services.investidor10 import Investidor10Service
from app.utils.redis_cache import get_cached_data
from datetime import datetime


class FII:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()

        def fetch_data():
            ticker_obj = yf.Ticker(self.ticker)
            return {
                "info": ticker_obj.info,
                "balance_sheet": ticker_obj.balance_sheet.to_dict(),
                "dividends": {
                    str(k.date()): float(v)
                    for k, v in ticker_obj.dividends.items()
                },
            }

        dados = get_cached_data(f"fii:{self.ticker}", 900, fetch_data)
        self._info = dados["info"]
        self._balance_sheet = pd.DataFrame(dados["balance_sheet"])
        self._dividends = pd.Series(dados["dividends"])
        self._i10_service = None

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
        if self.valor_patrimonial is None or self.cotas_emitidas is None:
            i10 = self.i10_service
            return round(self.cotacao / i10.get_pvp(), 2)
        return round(self.valor_patrimonial / self.cotas_emitidas, 2)

    @property
    def cotacao(self):
        if 'currentPrice' in self.info:
            return self.info['currentPrice']
        return self.info.get('ask', 0)

    @property
    def pvp(self):
        return round(self.cotacao / self.vpa, 2)


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





def convert_unix_date(unix_date: int) -> str:
    """
    Converte uma data em formato Unix timestamp para string no formato dd/mm.
    """
    date_time = datetime.fromtimestamp(unix_date)
    return date_time.strftime('%d/%m')


def get_investidor10(ticker: str) -> Investidor10Service:
    """
    Inicializa scraping no Investidor10 a partir do ticker.
    """
    ticker = ticker.split(".")[0]
    return Investidor10Service(ticker)


def main():
    fii = FII('VGIA11.SA')

    print(f"Ticker: {fii.ticker}")
    print(f"Valor Patrimonial: {fii.valor_patrimonial}")
    print(f"Cotas Emitidas: {fii.cotas_emitidas}")
    print(f"VPA: {fii.vpa}")
    print(f"Cotação: {fii.cotacao}")
    print(f"P/VP: {fii.pvp}")
    print(f"Dividend Yield: {fii.dividend_yield}")
    print(f"Dividendo estimado: {fii.dividendo_estimado}")
    print(f"Risco de Liquidez: {fii.risco_liquidez}")
    print(f"Risco de Tamanho: {fii.risco_tamanho}")
    print(f"Risco de Preço e Volatilidade: {fii.risco_preco_volatilidade}")
    print(f"Risco de Rendimento: {fii.risco_rendimento}")
    print(f"Overall Risk: {fii.overall_risk(10)}")
    print(f"Histórico de Dividendos: {fii.historico_dividendos}")
    print(f"Segmento: {fii.segmento()}")
    # print(fii.info) # para debug completo


if __name__ == "__main__":
    main()
