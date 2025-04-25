from math import sqrt

import pandas as pd
import yfinance as yf
from scipy.stats import trim_mean


class Acao:
    def __init__(self, ticker):
        self.ticker = ticker
        self.acao = yf.Ticker(ticker)
        self.adj_close = yf.download(ticker, period="5y", progress=False, auto_adjust=False)

    def media_ponderada_fechamento(self, ano):
        return trim_mean(self.adj_close.loc[f"{ano}-"].tail(30).values, proportiontocut=0.1)

    @property
    def teto_cotacao_lucro(self):
        try:
            dates = list(self.acao.income_stmt.loc['Net Income'].dropna().tail(5).index.year)
            lucro = list(self.acao.income_stmt.loc['Net Income'].dropna().tail(5).values)
            cotacoes = [round(float(self.media_ponderada_fechamento(d)[0]), 2) for d in dates]
            # invertendo a ordem das listas
            dates = dates[::-1]
            lucro = lucro[::-1]
            cotacoes = cotacoes[::-1]

            # montar dict
            dados = {
                'Ano': dates,
                'Lucro Liquido': lucro,
                'Cotacao': cotacoes
            }

            #dataframe
            df = pd.DataFrame(dados)

            # Normalizar o valor do lucro liquido para escala de cotacao
            ultimo_lucro = df['Lucro Liquido'].iloc[-1]
            min_cotacao = df['Cotacao'].min()
            max_cotacao = df['Cotacao'].max()
            min_lucro = df['Lucro Liquido'].min()
            max_lucro = df['Lucro Liquido'].max()

            normalizado = round(min_cotacao + (ultimo_lucro - min_lucro) * (max_cotacao - min_cotacao) / (max_lucro - min_lucro),2)


            # verificar se o ultimo lucro liquido foi negativo
            if ultimo_lucro < 0 and self.acao.info['previousClose'] < 1:

                ajuste = round(sqrt(normalizado * self.acao.info['previousClose']) / (self.acao.info['previousClose']*100),2)
                return min(ajuste, normalizado)

            if ultimo_lucro < 0 and self.acao.info['previousClose'] > 1:
                ajuste = round(sqrt(normalizado * self.acao.info['previousClose']), 2)
                return min(ajuste, normalizado)


            # Calcular o valor normalizada do ultimo lucro na escala de cotaçao
            return normalizado
        except Exception as e:
            print(f"Erro: {e}")
            return None



    @property
    def cotacao(self):
        if 'currentPrice' in self.acao.info:
            return self.acao.info['currentPrice']
        if 'previousClose' in self.acao.info:
            return self.acao.info['previousClose']
        return self.adj_close.iloc[-1]

    @property
    def earning_yield(self):
        if 'trailingPE' in self.acao.info:
            return (1/self.acao.info['trailingPE'])*100
        return 0

    @property
    def pl(self):
        if 'trailingPE' in self.acao.info:
            return self.acao.info['trailingPE']
        return None


    @property
    def margem_liquida(self):
        return self.acao.info['profitMargins'] if 'profitMargins' in self.acao.info else None

    @property
    def liquidez_corrente(self):
        return self.acao.info['quickRatio'] if 'quickRatio' in self.acao.info else None

    @property
    def div_ebitda(self):
        if 'totalDebt' not in self.acao.info or 'ebitda' not in self.acao.info:
            return None
        return self.acao.info['totalDebt'] / self.acao.info['ebitda']


    @property
    def dy(self):
        return self.acao.info['dividendYield']/100 if 'dividendYield' in self.acao.info else 0

    @property
    def roe(self):
        return self.acao.info['returnOnEquity'] if 'returnOnEquity' in self.acao.info else None

    @property
    def recomendacao(self):
        return self.acao.info['recommendationKey'] if 'recommendationKey' in self.acao.info else None

    # @property
    # def nota(self):
    #     return score.evaluate_company(self.acao)

    @property
    def lucro(self):
        return self.acao.info['profitMargins'] if 'profitMargins' in self.acao.info else None

    @property
    def receita(self):
        return self.acao.info['revenueGrowth'] if 'revenueGrowth' in self.acao.info else None

    @property
    def dy_estimado(self):
        if 'dividendRate' in self.acao.info and 'currentPrice' in self.acao.info:
            return self.acao.info['dividendRate'] / self.acao.info['currentPrice']
        return 0

    @property
    def risco_geral(self):
        return self.acao.info['overallRisk'] if 'overallRisk' in self.acao.info else 10

    @property
    def free_float(self):
        if 'floatShares' in self.acao.info and 'impliedSharesOutstanding' in self.acao.info:
            return self.acao.info['floatShares'] / self.acao.info['impliedSharesOutstanding'] * 100
        return 0






def main():
    ativo = acao("VALE3.SA")
    print("Teto cotaçao x lucro:", ativo.teto_cotacao_lucro)
    # print("Cotacao:", ativo.cotacao)
    # print("Margem liquida:", ativo.margem_liquida)
    # print("Liquidez corrente:", ativo.liquidez_corrente)
    # print("Divida/EBITDA:", ativo.div_ebitda)
    # print("DY:", ativo.dy)
    # print("ROE:", ativo.roe)
    # print("Recomendacao:", ativo.recomendacao)
    # # print("Nota:", ativo.nota)
    # print("Lucro:", ativo.lucro)
    # print("DY estimado:", ativo.dy_estimado)
    # print("Risco geral:", ativo.risco_geral)
    # print("Free float:", ativo.free_float)



if __name__ == "__main__":
    main()

