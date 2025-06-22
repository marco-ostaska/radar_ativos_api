from datetime import datetime


from app.db.indicadores_ativos_db import IndicadoresAtivosDB
from app.services.fii_yf import FIIYahooService
from app.services.fiiscom import FiisComService
from app.services.indice_refresher import IndiceRefresher
from app.services.investidor10 import Investidor10Service




class FII:
    def __init__(self, ticker, force_update=False):
        self.ticker = ticker.upper()
        self.ticker_base = self.ticker.split(".")[0]
        self.yf = FIIYahooService(self.ticker, force=force_update)
        self.fiiscom = FiisComService(self.ticker_base, force=force_update)
        self.i10 = Investidor10Service(self.ticker_base, force=force_update)


    @property
    def info(self):
        return self.yf.info
    
    @property
    def dividends(self):
        return self.yf.dividends

    @property
    def valor_patrimonial(self):
        if self.yf.valor_patrimonial:
            return self.yf.valor_patrimonial
        return self.fiiscom.valor_patrimonial

    @property
    def cotas_emitidas(self):
        if self.yf.cotas_emitidas:
            return self.yf.cotas_emitidas
        return self.fiiscom.cotas_emitidas

    @property
    def vpa(self):
        if self.fiiscom.vpa:
            return self.fiiscom.vpa
        return self.yf.vpa

    @property
    def cotacao(self):
        if self.yf.cotacao:
            return self.yf.cotacao
        return self.fiiscom.cotacao

    @property
    def pvp(self):
        if self.i10.get_pvp():
            return self.i10.get_pvp()
        if self.fiiscom.pvp:
            return self.fiiscom.pvp
        return round(self.cotacao / self.vpa, 2) if self.vpa else None

    @property
    def dividend_yield(self):
        if self.fiiscom.dividend_yield:
            return self.fiiscom.dividend_yield
        if self.i10.get_dividend_yield():
            return self.i10.get_dividend_yield()
        return self.yf.dividend_yield

    @property
    def historico_dividendos(self):
        if self.fiiscom.historico_dividendos:
            return self.fiiscom.historico_dividendos
        return self.yf.historico_dividendos


    @property
    def dividendo_estimado(self):
        if self.fiiscom.dividendo_estimado:
            return self.fiiscom.dividendo_estimado *12
        return self.yf.dividendo_estimado

    


    @property
    def risco_liquidez(self):
        if self.fiiscom.risco_liquidez:
            return self.fiiscom.risco_liquidez
        return self.yf.risco_liquidez

    @property
    def risco_tamanho(self):
        if self.fiiscom.risco_tamanho:
            return self.fiiscom.risco_tamanho
        return self.yf.risco_tamanho

    @property
    def risco_preco_volatilidade(self):
        if self.fiiscom.risco_preco_volatilidade:
            return self.fiiscom.risco_preco_volatilidade
        return self.yf.risco_preco_volatilidade

    @property
    def risco_rendimento(self):
        if self.fiiscom.risco_rendimento:
            return self.fiiscom.risco_rendimento
        return self.yf.risco_rendimento

    def overall_risk(self) -> float:
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
            (self.risco_operacional(self.segmento()) * pesos["operacional"])
        )

        return round(min(max(overall_risk, 1), 10), 1)
    
    def segmento(self) -> str:
        """
        Retorna o tipo do FII (Fundo de Papel, Fundo de Tijolo, etc).
        """
        return self.i10.get_segmento()


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
        tipo = ativo.i10.get_segmento()
        spread = db.get_spread(tipo)
        indice_base = indices_service.melhor_indice()
        spread_total = spread + indice_base
        indices = indices_service.get_indices()

        dy_estimado = (ativo.dividendo_estimado /12) / ativo.cotacao * 100
        teto_div = (ativo.dividendo_estimado /12) / spread_total * 100
        real = dy_estimado - indices["ipca_atual"]
        potencial = round((((teto_div - ativo.cotacao) / ativo.cotacao)*100), 2)
        risco = round(11 - ativo.overall_risk(),1)
        score = evaluate_fii(ativo, indice_base)
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
        tipo = ativo.i10.get_segmento()
        spread = db.get_spread(tipo)
        indice_base = indices_service.melhor_indice()
        spread_total = spread + indice_base
        indices = indices_service.get_indices()

        dy_estimado = ativo.dividendo_estimado
        teto_div = (ativo.dividendo_estimado/12) / spread_total * 100
        real = dy_estimado - indices["ipca_atual"]
        potencial = round(((teto_div - ativo.cotacao) / ativo.cotacao) * 100, 2)
        risco = round(11 - ativo.overall_risk(), 1)
        cotas_necessarias = round(1000 / ativo.dividendo_estimado, 2)
        investimento_necessario = round(cotas_necessarias * ativo.cotacao, 2)

        return {
            "ticker": ativo.ticker.split(".")[0],
            "cotacao": round(ativo.cotacao, 2),
            "valor_patrimonial": round(ativo.valor_patrimonial, 2) if ativo.valor_patrimonial else None,
            "cotas_emitidas": int(ativo.cotas_emitidas) if ativo.cotas_emitidas else None,
            "vpa": round(ativo.vpa, 2) if ativo.vpa else None,
            "pvp": round(ativo.pvp, 2) if ativo.pvp else None,
            "dividend_yield": round(ativo.dividend_yield, 2) if ativo.dividend_yield else None,
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

# --- SCORE FUNCTIONS (consolidated from score_fii.py) ---

def score_dy(fii_data, indice_base: float) -> int:
    if fii_data.dividend_yield > (indice_base + 3) / 100:
        return 2
    if fii_data.dividend_yield == indice_base / 100:
        return 1
    return 0

def score_preco_medio(fii_data) -> int:
    if 'currentPrice' not in fii_data.info or 'fiftyDayAverage' not in fii_data.info or 'fiftyTwoWeekHigh' not in fii_data.info:
        return 0
    score = 0
    if fii_data.cotacao > fii_data.info['fiftyTwoWeekHigh'] * 0.90:
        score += 1
    if fii_data.cotacao < fii_data.info['fiftyDayAverage']:
        score += 1
    return score

def score_market_cap(fii_data) -> int:
    if 'marketCap' not in fii_data.info:
        return 0
    market_cap = fii_data.info['marketCap']
    if market_cap > 1e9:
        return 2
    if market_cap > 5e8:
        return 1
    return 0

def score_volume_medio(fii_data) -> int:
    if 'averageVolume' not in fii_data.info:
        return 0
    if fii_data.info['averageVolume'] > 50000:
        return 1
    return 0

def score_dividendos_crescentes(fii_data, indice_base: float) -> int:
    if fii_data.dividend_yield > (indice_base + 3) / 100:
        return 2
    if fii_data.dividend_yield > (indice_base + 1) / 100:
        return 1
    return 0

def score_vpa(fii_data) -> int:
    if fii_data.vpa > fii_data.cotacao:
        return 1
    if fii_data.vpa == fii_data.cotacao:
        return 0
    return -2

def bazin_score(fii_data, indice_base: float) -> int:
    if fii_data.cotacao < fii_data.dividendo_estimado / (indice_base + 3) * 100:
        return 1
    return -1

def calculate_max_score() -> int:
    return (
        2  # score_dy
        + 2  # score_preco_medio
        + 2  # score_market_cap
        + 1  # score_volume_medio
        + 2  # score_dividendos_crescentes
        + 1  # score_vpa
        + 1  # bazin_score
    )

def evaluate_fii(fii_data, indice_base: float) -> float:
    score = 0
    score += score_dy(fii_data, indice_base)
    score += score_preco_medio(fii_data)
    score += score_market_cap(fii_data)
    score += score_volume_medio(fii_data)
    score += score_dividendos_crescentes(fii_data, indice_base)
    score += score_vpa(fii_data)
    score += bazin_score(fii_data, indice_base)
    max_score = calculate_max_score()
    normalized_score = (score / max_score) * 10
    return round(normalized_score, 1)

def main():
    fii = FII('MAXR11.SA')
    # print("Dividendos:", fii.dividends)
    # print("Valor Patrimonial:", fii.valor_patrimonial)
    # print("Cotas Emitidas:", fii.cotas_emitidas)
    # print("VPA:", fii.vpa)
    # print("Cotação:", fii.cotacao)
    # print("P/VP:", fii.pvp)
    # print("Dividend Yield:", fii.dividend_yield)
    # print("Histórico de Dividendos:", fii.historico_dividendos)
    # print("Dividendo Estimado:", fii.dividendo_estimado)
    # print("Risco de Liquidez:", fii.risco_liquidez)
    # print("Risco de Tamanho:", fii.risco_tamanho)
    # print("Risco de Preço/Volatilidade:", fii.risco_preco_volatilidade)
    # print("Risco de Rendimento:", fii.risco_rendimento)
    # print("Segmento:", fii.segmento())
    # print("Risco Geral:", fii.overall_risk())

        
    print("\n--- Teste: RADAR (cache) ---")
    print(fii.get_radar())

    
    print("\n--- Teste: RADAR (forçando refresh) ---")
    print(fii.get_radar())

   

    print("\n--- Teste: DETALHADO ---")
    print(fii.get_detalhado())

if __name__ == "__main__":
    main()
