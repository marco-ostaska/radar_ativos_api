import requests
from bs4 import BeautifulSoup


class Investidor10Service:
    """
    Serviço para buscar dados de FIIs através do site Investidor10 usando requests.
    """

    BASE_URL = "https://investidor10.com.br/fiis/"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }

    def __init__(self, ticker: str):
        """
        Inicializa o serviço com o ticker desejado.

        :param ticker: Ticker do FII, ex: "HGLG11"
        """
        self.ticker = ticker.upper()
        self.soup = self._baixar_html()

    def _baixar_html(self) -> BeautifulSoup:
        """
        Realiza o download da página do FII no Investidor10.

        :return: Objeto BeautifulSoup com o HTML carregado
        """
        url = f"{self.BASE_URL}{self.ticker}"
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

    def get_cotacao(self) -> float | None:
        """
        Retorna a cotação atual do FII.

        :return: Cotação em float ou None se não encontrado
        """
        cotacao_span = self.soup.find('span', class_='value')
        if cotacao_span:
            cotacao = cotacao_span.text.strip().replace("R$ ", "").replace(",", ".")
            return float(cotacao)
        return None

    def get_dividend_yield(self) -> float | None:
        """
        Retorna o Dividend Yield atual do FII.

        :return: Dividend Yield em percentual ou None se não encontrado
        """
        tag = self.soup.find('span', title='Dividend Yield')
        if tag:
            value = tag.find_next('span').text.strip()
            return float(value.replace("%", "").replace(",", "."))
        return None

    def get_pvp(self) -> float | None:
        """
        Retorna o P/VP atual do FII.

        :return: P/VP como float ou None se não encontrado
        """
        tag = self.soup.find('span', title='P/VP')
        if tag:
            value = tag.find_next('span').text.strip()
            return float(value.replace(",", "."))
        return None


def main():
    """
    Testa a coleta de dados de um FII via Investidor10 usando requests.
    """
    try:
        fii_scraper = Investidor10Service("VGIA11")

        cotacao = fii_scraper.get_cotacao()
        dy = fii_scraper.get_dividend_yield()
        pvp = fii_scraper.get_pvp()

        print(f"Ticker: {fii_scraper.ticker}")
        print(f"Cotação: {cotacao if cotacao is not None else 'Não encontrado'}")
        print(f"Dividend Yield: {dy if dy is not None else 'Não encontrado'}%")
        print(f"P/VP: {pvp if pvp is not None else 'Não encontrado'}")

    except Exception as e:
        print(f"Erro ao acessar Investidor10: {e}")


if __name__ == "__main__":
    main()
