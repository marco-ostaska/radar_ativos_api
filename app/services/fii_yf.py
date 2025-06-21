import yfinance as yf
import pandas as pd
import numpy as np
from app.utils.redis_cache import get_cached_data

class FIIYahooService:
    def __init__(self, ticker: str, force: bool = False):
        self.ticker = ticker.upper()
        def fetch_data():
            fii_yf = yf.Ticker(self.ticker)
            return {
                "info": fii_yf.info,
                "dividends": fii_yf.dividends.to_dict(),
                "balance_sheet": fii_yf.balance_sheet.to_dict(),
            }
        data = get_cached_data(
            key=f"fii_yf:{self.ticker}",
            fetch_fn=fetch_data,
            force=force
        )
        self._info = data["info"]
        self._dividends = pd.Series(data["dividends"])
        self._balance_sheet = pd.DataFrame(data["balance_sheet"])

    @property
    def info(self):
        return self._info

    @property
    def dividends(self):
        return self._dividends

    @property
    def balance_sheet(self):
        return self._balance_sheet

    @property
    def valor_patrimonial(self):
        if 'Total Equity Gross Minority Interest' not in self._balance_sheet.index:
            return None
        return self._balance_sheet.loc['Total Equity Gross Minority Interest'].head(1).values[0]

    @property
    def cotas_emitidas(self):
        if 'Ordinary Shares Number' not in self._balance_sheet.index:
            return None
        valor = self._balance_sheet.loc['Ordinary Shares Number'].head(1).values[0]
        if np.isnan(valor):
            return None
        return valor

    @property
    def cotacao(self):
        if 'currentPrice' in self._info:
            return self._info['currentPrice']
        return self._info.get('ask', 0)

    @property
    def vpa(self):
        if self.valor_patrimonial is not None and self.cotas_emitidas is not None:
            return round(self.valor_patrimonial / self.cotas_emitidas, 2)
        return 0

    @property
    def pvp(self):
        if self.vpa:
            return round(self.cotacao / self.vpa, 2)
        return None

    @property
    def dividend_yield(self):
        if self.cotacao:
            return self._dividends.tail(12).sum() / self.cotacao
        return None

    @property
    def historico_dividendos(self):
        return {
            '1 mes': self._dividends.tail(1).sum(),
            '3 meses': self._dividends.tail(3).sum(),
            '6 meses': self._dividends.tail(6).sum(),
            '12 meses': self._dividends.tail(12).sum(),
        }

    @property
    def dividendo_estimado(self):
        tres_meses = self._dividends.tail(3).sum() / 3
        seis_meses = self._dividends.tail(6).sum() / 6
        if tres_meses < seis_meses:
            return tres_meses * 12
        return seis_meses * 12

    @property
    def risco_liquidez(self):
        volume = self._info.get("averageVolume", 0)
        try:
            if volume > 1_000_000:
                return 1
            elif volume > 200_000:
                return 5
            return 10
        except Exception:
            return 10

if __name__ == "__main__":
    ticker = "VGIA11.SA"
    fii = FIIYahooService(ticker, True)
    print(f"Ticker: {ticker}")
    print("Info:", fii.info)
    print("Cotação:", fii.cotacao)
    print("VPA:", fii.vpa)
    print("P/VP:", fii.pvp)
    print("Dividend Yield:", fii.dividend_yield)
    print("Histórico de Dividendos:", fii.historico_dividendos)
    print("Dividendo estimado:", fii.dividendo_estimado)
    print("Valor Patrimonial:", fii.valor_patrimonial)
    print("Cotas Emitidas:", fii.cotas_emitidas)
    print("Risco de Liquidez:", fii.risco_liquidez)
