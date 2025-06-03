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
    

    def get_info_from_table(self, field_name: str) -> str | None:
        """
        Busca informações específicas na tabela de indicadores.

        :param field_name: Nome do campo a buscar (ex: 'SEGMENTO')
        :return: Valor do campo ou None se não encontrado
        """
        table = self.soup.find('div', id='table-indicators')
        if not table:
            return None

        for cell in table.find_all('div', class_='cell'):
            label_span = cell.find('span', class_='d-flex justify-content-between align-items-center name')
            if label_span:
                label = label_span.get_text(strip=True).upper()
                if field_name.upper() in label:
                    value_div = cell.find('div', class_='value')
                    if value_div:
                        value_span = value_div.find('span')
                        if value_span:
                            return value_span.get_text(strip=True)
        return None

    def get_segmento(self) -> str | None:
        segmento = self.get_info_from_table("SEGMENTO")
        if segmento is None:
            return None
        
        if "fiagro" in segmento.lower():
            return "fiagro"
        
        if "brido" in segmento.lower():
            return "hibrido"
        
        if "infra" in segmento.lower():
            return "infra"
        
        if "stic" in segmento.lower():
            return "logistica"

        if "shopping" in segmento.lower():
            return "shopping"
        
        return "papel"

def main():
    """
    Testa a coleta de dados de um FII via Investidor10 usando requests.
    """
    try:
        fii_scraper = Investidor10Service("HSML11")  # Exemplo de ticker, substitua conforme necessário

        cotacao = fii_scraper.get_cotacao()
        dy = fii_scraper.get_dividend_yield()
        pvp = fii_scraper.get_pvp()

        print(f"Ticker: {fii_scraper.ticker}")
        print(f"Cotação: {cotacao if cotacao is not None else 'Não encontrado'}")
        print(f"Dividend Yield: {dy if dy is not None else 'Não encontrado'}%")
        print(f"P/VP: {pvp if pvp is not None else 'Não encontrado'}")
        print(f"Segmento: {fii_scraper.get_segmento() if fii_scraper.get_segmento() else 'Não encontrado'}")

    except Exception as e:
        print(f"Erro ao acessar Investidor10: {e}")


if __name__ == "__main__":
    main()
