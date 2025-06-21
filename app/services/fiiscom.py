import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pandas as pd
from app.utils.redis_cache import get_cached_data

class FiisComService:
    def __init__(self, ticker: str, force: bool = False):
        self.ticker = ticker.upper()
        self._dados = get_cached_data(
            key=f"fiiscom:{self.ticker}",
            fetch_fn=self._fetch_fiiscom_data,
            force=force
        )

    def _fetch_fiiscom_data(self):
        url = f"https://fiis.com.br/{self.ticker.lower()}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        h1 = soup.find("h1")
        nome = h1.get_text(strip=True) if h1 else ""
        descricao = ""
        desc_div = soup.find("div", class_="headerTicker__content__name")
        if desc_div and desc_div.find("p"):
            descricao = desc_div.find("p").get_text(strip=True)

        indicadores = []
        dividend_yield_html = None
        indicators = soup.find("div", class_="indicators")
        if indicators:
            for box in indicators.find_all("div", class_="indicators__box"):
                ps = box.find_all("p")
                valor = ""
                label = ""
                if len(ps) == 2:
                    valor = ps[0].find("b").get_text(strip=True) if ps[0].find("b") else ""
                    label = ps[1].get_text(strip=True)
                elif len(ps) == 1:
                    valor = ps[0].find("b").get_text(strip=True) if ps[0].find("b") else ""
                    label = ""
                indicadores.append((label, valor))
                if "Dividend Yield" in label and valor:
                    dividend_yield_html = float(valor.replace(",", ".").replace("%", "").strip())

        cotacao = ""
        min_52 = ""
        max_52 = ""
        valorizacao_12m = ""
        q_item = soup.find("div", class_="item quotation")
        if q_item:
            v = q_item.find("span", class_="value")
            cotacao = v.get_text(strip=True) if v else ""
        minmax = soup.find_all("div", class_="item min-max")
        if len(minmax) > 0:
            min_52 = minmax[0].find("span", class_="value").get_text(strip=True)
        if len(minmax) > 1:
            max_52 = minmax[1].find("span", class_="value").get_text(strip=True)
        val_item = soup.find("div", class_="item valorization")
        if val_item:
            v = val_item.find("span", class_="variation")
            valorizacao_12m = v.get_text(strip=True) if v else ""

        dividendos = []
        for bloco in soup.select(".yieldChart__table__bloco--rendimento"):
            linhas = bloco.find_all("div", class_="table__linha")
            if len(linhas) == 6:
                dividendos.append({
                    "tipo": linhas[0].get_text(strip=True),
                    "data_base": linhas[1].get_text(strip=True),
                    "data_pagamento": linhas[2].get_text(strip=True),
                    "cotacao_base": linhas[3].get_text(strip=True),
                    "dividend_yield": linhas[4].get_text(strip=True),
                    "rendimento": linhas[5].get_text(strip=True),
                })

        info = {}
        for p in soup.select(".moreInfo.wrapper p"):
            spans = p.find_all("span")
            if spans and p.find("b"):
                chave = spans[0].get_text(strip=True)
                valor = p.find("b").get_text(strip=True)
                info[chave] = valor

        jsonld_data = {}
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "InvestmentFund":
                    jsonld_data = data
            except Exception:
                pass

        indicadores_extras = {}
        for box in soup.select(".wrapper.indicators .indicators__box"):
            label = box.find_all("p")
            if len(label) > 1:
                key = label[1].get_text(strip=True)
                val = box.find("b").get_text(strip=True) if box.find("b") else ""
                indicadores_extras[key] = val

        return {
            "nome": nome,
            "descricao": descricao,
            "indicadores": indicadores,
            "cotacao_atual": cotacao,
            "min_52_semanas": min_52,
            "max_52_semanas": max_52,
            "valorizacao_12_meses": valorizacao_12m,
            "dividendos": dividendos,
            "info_extra": info,
            "jsonld": jsonld_data,
            "indicadores_extras": indicadores_extras,
            "dividend_yield_html": dividend_yield_html,
        }

    @property
    def dados(self):
        return self._dados

    @property
    def dividends(self):
        try:
            data = {
                d["data_base"]: float(d["rendimento"].replace("R$", "").replace(",", ".").strip())
                for d in self._dados["dividendos"]
            }
            return pd.Series(data)
        except Exception:
            return pd.Series()

    @property
    def valor_patrimonial(self):
        try:
            if "amount" in self._dados["jsonld"]:
                return float(self._dados["jsonld"]["amount"]["value"])
            val = self._dados["info_extra"].get("Patrimônio", "")
            return float(val.replace("R$", "").replace(".", "").replace(",", "."))
        except Exception:
            return None

    @property
    def cotas_emitidas(self):
        try:
            val = self._dados["info_extra"].get("Número de Cotas", "")
            return int(val.replace(".", ""))
        except Exception:
            return None

    @property
    def vpa(self):
        try:
            if "Val. Patrimonial p/Cota" in self._dados["indicadores_extras"]:
                return float(self._dados["indicadores_extras"]["Val. Patrimonial p/Cota"].replace(",", "."))
            if self.valor_patrimonial and self.cotas_emitidas:
                return round(self.valor_patrimonial / self.cotas_emitidas, 2)
        except Exception:
            return None

    @property
    def cotacao(self):
        try:
            return float(self._dados["cotacao_atual"].replace(",", "."))
        except Exception:
            return None

    @property
    def pvp(self):
        try:
            return round(self.cotacao / self.vpa, 2)
        except Exception:
            return None

    @property
    def dividend_yield(self):
        """Retorna o Dividend Yield exatamente como aparece no HTML (ex: 17.01 para 17,01%)."""
        return self._dados.get("dividend_yield_html")

    @property
    def historico_dividendos(self):
        try:
            divs = [float(d["rendimento"].replace("R$", "").replace(",", ".").strip()) for d in self._dados["dividendos"]]
            return {
                '1 mes': sum(divs[:1]),
                '3 meses': sum(divs[:3]),
                '6 meses': sum(divs[:6]),
                '12 meses': sum(divs[:12]),
            }
        except Exception:
            return {}

    @property
    def dividendo_estimado(self):
        try:
            divs = [float(d["rendimento"].replace("R$", "").replace(",", ".").strip()) for d in self._dados["dividendos"]]
            tres = sum(divs[:3]) / 3 if len(divs) >= 3 else 0
            seis = sum(divs[:6]) / 6 if len(divs) >= 6 else 0
            if tres < seis:
                return tres * 12
            return seis * 12
        except Exception:
            return None

    @property
    def nome(self):
        return self._dados["nome"]

    @property
    def descricao(self):
        return self._dados["descricao"]

    @property
    def segmento(self):
        return self._dados["info_extra"].get("Segmento", "") or self._dados["jsonld"].get("category", "")

    @property
    def cnpj(self):
        return self._dados["info_extra"].get("CNPJ", "")

    @property
    def administrador(self):
        adm = self._dados["jsonld"].get("brand", {}).get("name", "")
        if not adm:
            adm = self._dados["info_extra"].get("Administrador", "")
        return adm

    @property
    def numero_cotistas(self):
        val = self._dados["indicadores_extras"].get("N° de Cotistas", "")
        try:
            return int(val.replace(".", ""))
        except Exception:
            return val

    @property
    def participacao_ifix(self):
        val = self._dados["indicadores_extras"].get("Participações no IFIX", "")
        try:
            return float(val.replace("%", "").replace(",", "."))
        except Exception:
            return val

    @property
    def liquidez_media(self):
        val = self._dados["indicadores_extras"].get("Liquidez média diária", "")
        try:
            return float(val.replace("M", "e6").replace(".", "").replace(",", "."))
        except Exception:
            return val

    @property
    def valor_em_caixa(self):
        val = self._dados["indicadores_extras"].get("Valor em caixa", "")
        try:
            return float(val.replace("M", "e6").replace(".", "").replace(",", "."))
        except Exception:
            return val

    @property
    def risco_liquidez(self):
        val = self._dados["indicadores_extras"].get("Liquidez média diária", "")
        try:
            volume = float(val.replace("M", "e6").replace(".", "").replace(",", "."))
            if volume > 1_000_000:
                return 1
            elif volume > 200_000:
                return 5
            return 10
        except Exception:
            return 10

if __name__ == "__main__":
    fii = FiisComService("vgia11", True)
    print("Nome:", fii.nome)
    print("Descrição:", fii.descricao)
    print("Cotação:", fii.cotacao)
    print("Dividend Yield (anualizado):", fii.dividend_yield)
    print("Histórico de Dividendos:", fii.historico_dividendos)
    print("Dividendo estimado:", fii.dividendo_estimado)
    print("Valor Patrimonial:", fii.valor_patrimonial)
    print("Cotas Emitidas:", fii.cotas_emitidas)
    print("VPA:", fii.vpa)
    print("P/VP:", fii.pvp)
    print("Segmento:", fii.segmento)
    print("Liquidez média diária:", fii.liquidez_media)
    print("Valor em caixa:", fii.valor_em_caixa)
    print("Número de cotistas:", fii.numero_cotistas)
    print("Participação IFIX:", fii.participacao_ifix)
    print("Administrador:", fii.administrador)
    print("CNPJ:", fii.cnpj)
    print("Risco de Liquidez:", fii.risco_liquidez)
