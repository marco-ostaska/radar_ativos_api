from math import sqrt
import pandas as pd
import yfinance as yf
from app.utils.redis_cache import get_cached_data
from scipy.stats import trim_mean

def safe_dict(df: pd.DataFrame) -> dict:
    """
    Garante que colunas e índices sejam serializáveis como JSON.
    Converte Timestamp e colunas em string.
    """
    df = df.copy()
    df.columns = df.columns.map(str)
    df.index = df.index.map(str)
    return df.to_dict(orient="index")


class Acao:
    def __init__(self, ticker: str, force: bool = False):
        self.ticker = ticker.upper()

        dados = get_cached_data(
            f"acao:{self.ticker}",
            None,
            lambda: {
                "info": yf.Ticker(self.ticker).info,
                "income_stmt": safe_dict(yf.Ticker(self.ticker).income_stmt),
                "adj_close": safe_dict(yf.download(self.ticker, period="5y", progress=False, auto_adjust=False))
            },
            force=force
        )

        self.info = dados["info"]
        self.income_stmt = pd.DataFrame.from_dict(dados["income_stmt"], orient="index")
        self.adj_close = pd.DataFrame.from_dict(dados["adj_close"], orient="index")

    def media_ponderada_fechamento(self, ano: int) -> float | None:
        #return trim_mean(self.adj_close.loc[f"{ano}-"].tail(30).values, proportiontocut=0.1)
        mask = pd.to_datetime(self.adj_close.index).year == ano
      
        return trim_mean(self.adj_close.loc[mask].tail(30).values, proportiontocut=0.1)


    def calcular_teto_cotacao_lucro(self) -> float | None:
        income = self.income_stmt.loc['Net Income'].dropna().tail(5)
        print("income:", income)
        datas = list(pd.to_datetime(income.index).year)
        print("datas:", datas)
        lucros = list(income.values)
        print("lucros:", lucros)
        cotacoes = [self.media_ponderada_fechamento(ano) for ano in datas]
        print("cotacoes:", cotacoes)
        datas, lucros, cotacoes = datas[::-1], lucros[::-1], cotacoes[::-1]

        try:
            income = self.income_stmt.loc['Net Income'].dropna().tail(5)
            datas = list(pd.to_datetime(income.index).year)
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
            previous_close = self.info.get("previousClose") or self.info.get("regularMarketPreviousClose") or 0


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
        if 'currentPrice' in self.info:
            return self.info['currentPrice']
        if 'previousClose' in self.info:
            return self.info['previousClose']
        if 'regularMarketPrice' in self.info:
            return self.info['regularMarketPrice']
        try:
            return self.adj_close.iloc[-1]['Close']
        except Exception:
            print("Erro:", self.info)
            return None

    @property
    def earning_yield(self) -> float:
        if 'trailingPE' in self.info:
            return (1 / self.info['trailingPE']) * 100
        return 0

    @property
    def pl(self) -> float | None: return self.info.get('trailingPE')
    @property
    def margem_liquida(self) -> float | None: return self.info.get('profitMargins')
    @property
    def liquidez_corrente(self) -> float | None: return self.info.get('quickRatio')
    @property
    def div_ebitda(self) -> float | None:
        if 'totalDebt' not in self.info or 'ebitda' not in self.info: return None
        return self.info['totalDebt'] / self.info['ebitda']
    @property
    def dy(self) -> float: return self.info.get('dividendYield', 0) / 100
    @property
    def roe(self) -> float | None: return self.info.get('returnOnEquity')
    @property
    def recomendacao(self) -> str | None: return self.info.get('recommendationKey')
    @property
    def lucro(self) -> float | None: return self.info.get('profitMargins')
    @property
    def receita(self) -> float | None: return self.info.get('revenueGrowth')
    @property
    def dy_estimado(self) -> float:
        if 'dividendRate' in self.info and 'currentPrice' in self.info:
            return self.info['dividendRate'] / self.info['currentPrice']
        return 0
    @property
    def risco_geral(self) -> int: return self.info.get('overallRisk', 10)
    @property
    def free_float(self) -> float:
        if 'floatShares' in self.info and 'impliedSharesOutstanding' in self.info:
            return (self.info['floatShares'] / self.info['impliedSharesOutstanding']) * 100
        return 0
    @property
    def lucro_liquido(self) -> float | None: return self.info.get('netIncomeToCommon')
    @property
    def valor_mercado(self) -> float | None: return self.info.get('marketCap')
    @property
    def vpa(self) -> float | None: return self.info.get('bookValue')
    @property
    def lpa(self) -> float | None: return self.info.get('trailingEps')


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
