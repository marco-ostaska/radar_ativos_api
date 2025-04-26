from math import sqrt
from datetime import datetime

import pandas as pd
import yfinance as yf
from scipy.stats import trim_mean


class Acao:
    """
    Representa uma ação consultada via Yahoo Finance (yfinance).
    Oferece diversos indicadores financeiros para análise fundamentalista.
    """

    def __init__(self, ticker: str):
        """
        Inicializa o objeto Acao com um ticker específico.

        :param ticker: Código da ação (ex: "VALE3.SA")
        """
        self.ticker = ticker.upper()
        self.acao = yf.Ticker(self.ticker)
        self.adj_close = yf.download(self.ticker, period="5y", progress=False, auto_adjust=False)

    def media_ponderada_fechamento(self, ano: int) -> float:
        """
        Calcula a média aparada dos fechamentos do ano fornecido.

        :param ano: Ano de referência
        :return: Média aparada
        """
        return trim_mean(self.adj_close.loc[f"{ano}-"].tail(30).values, proportiontocut=0.1)

    def calcular_teto_cotacao_lucro(self) -> float | None:
        """
        Estima o teto da cotação com base nos lucros históricos.

        :return: Teto calculado ou None
        """
        try:
            income = self.acao.income_stmt.loc['Net Income'].dropna().tail(5)
            datas = list(income.index.year)
            lucros = list(income.values)
            cotacoes = [float(self.media_ponderada_fechamento(ano)[0]) for ano in datas]

            datas, lucros, cotacoes = datas[::-1], lucros[::-1], cotacoes[::-1]

            df = pd.DataFrame({
                "Ano": datas,
                "Lucro Liquido": lucros,
                "Cotacao": cotacoes,
            })

            ultimo_lucro = df["Lucro Liquido"].iloc[-1]
            min_cot = df["Cotacao"].min()
            max_cot = df["Cotacao"].max()
            min_lucro = df["Lucro Liquido"].min()
            max_lucro = df["Lucro Liquido"].max()

            normalizado = round(min_cot + (ultimo_lucro - min_lucro) * (max_cot - min_cot) / (max_lucro - min_lucro), 2)

            previous_close = self.acao.info.get("previousClose", 0)

            if ultimo_lucro < 0:
                ajuste = (
                    round(sqrt(normalizado * previous_close) / (previous_close * 100), 2)
                    if previous_close < 1 else
                    round(sqrt(normalizado * previous_close), 2)
                )
                return min(ajuste, normalizado)

            return normalizado
        except Exception:
            return None

    @property
    def cotacao(self) -> float:
        """Cotação atual."""
        if 'currentPrice' in self.acao.info:
            return self.acao.info['currentPrice']
        if 'previousClose' in self.acao.info:
            return self.acao.info['previousClose']
        return self.adj_close.iloc[-1]

    @property
    def earning_yield(self) -> float:
        """Earning yield (inverso do P/L)."""
        if 'trailingPE' in self.acao.info:
            return (1 / self.acao.info['trailingPE']) * 100
        return 0

    @property
    def pl(self) -> float | None:
        """P/L (Preço/Lucro)."""
        return self.acao.info.get('trailingPE')

    @property
    def margem_liquida(self) -> float | None:
        """Margem líquida."""
        return self.acao.info.get('profitMargins')

    @property
    def liquidez_corrente(self) -> float | None:
        """Liquidez corrente (quick ratio)."""
        return self.acao.info.get('quickRatio')

    @property
    def div_ebitda(self) -> float | None:
        """Dívida líquida sobre EBITDA."""
        if 'totalDebt' not in self.acao.info or 'ebitda' not in self.acao.info:
            return None
        return self.acao.info['totalDebt'] / self.acao.info['ebitda']

    @property
    def dy(self) -> float:
        """Dividend Yield atual (decimal, ex: 0.05 para 5%)."""
        return self.acao.info.get('dividendYield', 0) / 100

    @property
    def roe(self) -> float | None:
        """Return on Equity (ROE)."""
        return self.acao.info.get('returnOnEquity')

    @property
    def recomendacao(self) -> str | None:
        """Recomendação de analistas (buy, hold, sell)."""
        return self.acao.info.get('recommendationKey')

    @property
    def lucro(self) -> float | None:
        """Lucro (profit margins)."""
        return self.acao.info.get('profitMargins')

    @property
    def receita(self) -> float | None:
        """Crescimento de receita."""
        return self.acao.info.get('revenueGrowth')

    @property
    def dy_estimado(self) -> float:
        """Dividend yield projetado."""
        if 'dividendRate' in self.acao.info and 'currentPrice' in self.acao.info:
            return self.acao.info['dividendRate'] / self.acao.info['currentPrice']
        return 0

    @property
    def risco_geral(self) -> int:
        """Risco geral."""
        return self.acao.info.get('overallRisk', 10)

    @property
    def free_float(self) -> float:
        """Percentual de ações em circulação (free float)."""
        if 'floatShares' in self.acao.info and 'impliedSharesOutstanding' in self.acao.info:
            return (self.acao.info['floatShares'] / self.acao.info['impliedSharesOutstanding']) * 100
        return 0

    @property
    def lucro_liquido(self) -> float | None:
        """Lucro líquido (Net Income To Common)."""
        return self.acao.info.get('netIncomeToCommon')

    @property
    def valor_mercado(self) -> float | None:
        """Valor de mercado."""
        return self.acao.info.get('marketCap')

    @property
    def vpa(self) -> float | None:
        """Valor patrimonial por ação (Book Value)."""
        return self.acao.info.get('bookValue')

    @property
    def lpa(self) -> float | None:
        """Lucro por ação (Trailing EPS)."""
        return self.acao.info.get('trailingEps')


def main():
    ativo = Acao("VALE3.SA")
    print("Ticker:", ativo.ticker)
    print("Cotação:", ativo.cotacao)
    print("Teto por lucro:", ativo.calcular_teto_cotacao_lucro())
    print("Lucro líquido:", ativo.lucro_liquido)
    print("Valor mercado:", ativo.valor_mercado)
    print("VPA:", ativo.vpa)
    print("LPA:", ativo.lpa)
    print("Dividend Yield estimado:", ativo.dy_estimado)
    print("Earning Yield:", ativo.earning_yield)
    print("P/L:", ativo.pl)
    print("Margem líquida:", ativo.margem_liquida)
    print("ROE:", ativo.roe)
    print("Free Float:", ativo.free_float)


if __name__ == "__main__":
    main()
