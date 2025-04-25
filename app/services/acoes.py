from math import sqrt

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
        self.ticker = ticker
        self.acao = yf.Ticker(ticker)
        self.adj_close = yf.download(ticker, period="5y", progress=False, auto_adjust=False)

    def media_ponderada_fechamento(self, ano: int) -> float:
        """
        Calcula a média aparada (trimmed mean) dos preços de fechamento ajustados
        dos últimos 30 dias do ano fornecido.

        :param ano: Ano de referência (ex: 2023)
        :return: Média aparada do fechamento
        """
        return trim_mean(self.adj_close.loc[f"{ano}-"].tail(30).values, proportiontocut=0.1)

    def calcular_teto_cotacao_lucro(self) -> float | None:
        """
        Estima o teto de cotação com base na evolução dos lucros e cotações históricas.
        Aplica normalização e ajuste para lucro negativo.

        :return: Valor estimado do teto de cotação ou None em caso de erro
        """
        try:
            income = self.acao.income_stmt.loc['Net Income'].dropna().tail(5)
            dates = list(income.index.year)
            lucro = list(income.values)
            cotacoes = [round(float(self.media_ponderada_fechamento(d)[0]), 2) for d in dates]

            dates, lucro, cotacoes = dates[::-1], lucro[::-1], cotacoes[::-1]

            df = pd.DataFrame({
                'Ano': dates,
                'Lucro Liquido': lucro,
                'Cotacao': cotacoes
            })

            ultimo_lucro = df['Lucro Liquido'].iloc[-1]
            min_cotacao = df['Cotacao'].min()
            max_cotacao = df['Cotacao'].max()
            min_lucro = df['Lucro Liquido'].min()
            max_lucro = df['Lucro Liquido'].max()

            normalizado = round(min_cotacao + (ultimo_lucro - min_lucro) * (max_cotacao - min_cotacao) / (max_lucro - min_lucro), 2)

            previous_close = self.acao.info.get('previousClose', 0)
            if ultimo_lucro < 0:
                ajuste = (
                    round(sqrt(normalizado * previous_close) / (previous_close * 100), 2)
                    if previous_close < 1 else
                    round(sqrt(normalizado * previous_close), 2)
                )
                return min(ajuste, normalizado)

            return normalizado

        except Exception as e:
            raise RuntimeError(f"Erro ao calcular teto de cotação lucro: {e}")

    @property
    def cotacao(self) -> float:
        """Retorna a cotação atual ou mais recente da ação."""
        if 'currentPrice' in self.acao.info:
            return self.acao.info['currentPrice']
        if 'previousClose' in self.acao.info:
            return self.acao.info['previousClose']
        return self.adj_close.iloc[-1]

    @property
    def earning_yield(self) -> float:
        """Retorna o earning yield atual da ação."""
        if 'trailingPE' in self.acao.info:
            return (1 / self.acao.info['trailingPE']) * 100
        return 0

    @property
    def pl(self) -> float | None:
        """Retorna o P/L (Price/Earnings) atual."""
        return self.acao.info.get('trailingPE')

    @property
    def margem_liquida(self) -> float | None:
        """Retorna a margem líquida da empresa."""
        return self.acao.info.get('profitMargins')

    @property
    def liquidez_corrente(self) -> float | None:
        """Retorna a liquidez corrente (quick ratio) da empresa."""
        return self.acao.info.get('quickRatio')

    @property
    def div_ebitda(self) -> float | None:
        """Retorna a razão Dívida / EBITDA."""
        if 'totalDebt' not in self.acao.info or 'ebitda' not in self.acao.info:
            return None
        return self.acao.info['totalDebt'] / self.acao.info['ebitda']

    @property
    def dy(self) -> float:
        """Retorna o dividend yield atual em decimal (ex: 0.05 para 5%)."""
        return self.acao.info.get('dividendYield', 0) / 100

    @property
    def roe(self) -> float | None:
        """Retorna o Return on Equity (ROE) da empresa."""
        return self.acao.info.get('returnOnEquity')

    @property
    def recomendacao(self) -> str | None:
        """Retorna a recomendação atual de analistas (buy, hold, etc)."""
        return self.acao.info.get('recommendationKey')

    @property
    def lucro(self) -> float | None:
        """Retorna a margem de lucro."""
        return self.acao.info.get('profitMargins')

    @property
    def receita(self) -> float | None:
        """Retorna o crescimento de receita da empresa."""
        return self.acao.info.get('revenueGrowth')

    @property
    def dy_estimado(self) -> float:
        """Retorna o dividend yield estimado com base na razão e preço atual."""
        if 'dividendRate' in self.acao.info and 'currentPrice' in self.acao.info:
            return self.acao.info['dividendRate'] / self.acao.info['currentPrice']
        return 0

    @property
    def risco_geral(self) -> int:
        """Retorna o risco geral da empresa (se disponível)."""
        return self.acao.info.get('overallRisk', 10)

    @property
    def free_float(self) -> float:
        """Retorna o percentual de ações em circulação (free float)."""
        if 'floatShares' in self.acao.info and 'impliedSharesOutstanding' in self.acao.info:
            return (self.acao.info['floatShares'] / self.acao.info['impliedSharesOutstanding']) * 100
        return 0


def main():
    ativo = Acao("KEPL3.SA")
    print("Ticker:", ativo.ticker)
    print("Teto cotação x lucro:", ativo.calcular_teto_cotacao_lucro())
    print("Cotação:", ativo.cotacao)
    print("Margem líquida:", ativo.margem_liquida)
    print("Liquidez corrente:", ativo.liquidez_corrente)
    print("Dívida/EBITDA:", ativo.div_ebitda)
    print("DY:", ativo.dy)
    print("ROE:", ativo.roe)
    print("Recomendação:", ativo.recomendacao)
    print("Lucro:", ativo.lucro)
    print("DY estimado:", ativo.dy_estimado)
    print("Risco geral:", ativo.risco_geral)
    print("Free float:", ativo.free_float)


if __name__ == "__main__":
    main()
