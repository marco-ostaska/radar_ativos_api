from datetime import datetime

import numpy as np
import yfinance as yf

from app.services.investidor10 import Investidor10Service


class FII:
    """
    Classe para manipular dados de um Fundo Imobiliário (FII).
    """

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.fii = yf.Ticker(self.ticker)

    @property
    def info(self):
        return self.fii.info

    @property
    def valor_patrimonial(self):
        if 'Total Equity Gross Minority Interest' not in self.fii.balance_sheet.index:
            return None
        return self.fii.balance_sheet.loc['Total Equity Gross Minority Interest'].head(1).values[0]

    @property
    def cotas_emitidas(self):
        if 'Ordinary Shares Number' not in self.fii.balance_sheet.index:
            return None
        valor = self.fii.balance_sheet.loc['Ordinary Shares Number'].head(1).values[0]
        if np.isnan(valor):
            return None
        return valor

    @property
    def vpa(self):
        if self.valor_patrimonial is None or self.cotas_emitidas is None:
            i10 = get_investidor10(self.ticker)
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
    def dividends(self):
        return self.fii.dividends

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
        volume = self.info.get("averageVolume", 0)
        if volume > 50000:
            return 1
        if volume > 20000:
            return 5
        return 10

    @property
    def risco_tamanho(self):
        market_cap = self.info.get("marketCap", 0)
        if market_cap < 500_000_000:
            return 5
        return 1

    @property
    def risco_preco_volatilidade(self):
        variacao_52w = self.info.get("52WeekChange", 0)
        if variacao_52w < -0.15:
            return 10
        if variacao_52w < -0.05:
            return 5
        return 1

    @property
    def risco_rendimento(self):
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
    fii = FII('HSML11.SA')

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
    print(f"Overall Risk: {fii.overall_risk(3)}")
    print(f"Histórico de Dividendos: {fii.historico_dividendos}")
    # print(fii.info) # para debug completo


if __name__ == "__main__":
    main()
