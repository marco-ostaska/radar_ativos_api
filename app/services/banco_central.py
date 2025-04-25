import json
from datetime import datetime

import pandas as pd
import requests


class Indices:
    """
    Classe base para buscar e tratar séries históricas de índices do Banco Central do Brasil.
    """

    def __init__(self, anos_hist: int):
        self.anos_hist = anos_hist
        self.df = None

    def get_url(self, codigo_serie: int) -> str:
        """
        Gera a URL de consulta na API do Banco Central.

        :param codigo_serie: Código da série do Banco Central
        :return: URL formatada para requisição
        """
        ontem = datetime.now() - pd.Timedelta(days=1)
        data_inicio = f"{ontem.day}/{ontem.month}/{ontem.year - self.anos_hist}"
        data_final = f"{ontem.day}/{ontem.month}/{ontem.year}"
        url = (
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?"
            f"formato=json&dataInicial={data_inicio}&dataFinal={data_final}"
        )
        return url

    def parse(self, codigo_serie: int, indice: str) -> pd.DataFrame:
        """
        Faz a requisição e parse da série histórica.

        :param codigo_serie: Código da série no Banco Central
        :param indice: Nome da coluna que será atribuída no DataFrame
        :return: DataFrame tratado
        """
        if self.df is None:
            url = self.get_url(codigo_serie)
            response = requests.get(url)
            response.raise_for_status()
            data = json.loads(response.text)
            df = pd.DataFrame(data)
            df.rename(columns={"data": "date"}, inplace=True)
            df["date"] = pd.to_datetime(df["date"], format='%d/%m/%Y')
            df.set_index('date', inplace=True)
            df["valor"] = df["valor"].str.replace(',', '.').astype(float)
            df.rename(columns={"valor": indice}, inplace=True)
            self.df = df
        return self.df


class SELIC(Indices):
    """
    Classe para tratamento da série histórica da taxa SELIC.
    """

    def __init__(self, anos_hist: int):
        super().__init__(anos_hist)
        self.codigo_serie = 11
        self.indice = "Selic"

    def media_anual(self) -> float:
        """
        Retorna a média anualizada da taxa SELIC.

        :return: Média anual em percentual
        """
        dias_uteis = 22
        media = self.parse(self.codigo_serie, self.indice).mean().dropna().values[0] * dias_uteis * 12
        return round(media, 2)

    def media_ganho_real(self) -> float:
        """
        Retorna a média anual líquida de IR (15%).

        :return: Média líquida em percentual
        """
        return round(self.media_anual() * (1 - 0.15), 2)

    def atual(self) -> float:
        """
        Retorna a taxa SELIC anualizada atual.

        :return: Taxa atual em percentual
        """
        taxa_diaria = self.parse(self.codigo_serie, self.indice).iloc[-1].values[0] / 100
        return round(((1 + taxa_diaria) ** 252 - 1) * 100, 2)


class IPCA(Indices):
    """
    Classe para tratamento da série histórica do índice IPCA.
    """

    def __init__(self, anos_hist: int):
        super().__init__(anos_hist)
        self.codigo_serie = 10844
        self.indice = "IPCA"

    def media_anual(self) -> float:
        """
        Retorna a média anual do IPCA.

        :return: Média anual em percentual
        """
        media = self.parse(self.codigo_serie, self.indice).mean().dropna().values[0] * 12
        return round(media, 2)

    def media_ganho_real(self) -> float:
        """
        Estima o ganho real médio do IPCA considerando ajuste.

        :return: Ganho real médio em percentual
        """
        return self.media_anual() + 2


def taxa_livre_risco(anos_hist: int) -> float:
    """
    Calcula a taxa de livre de risco, comparando SELIC e IPCA.

    :param anos_hist: Número de anos históricos para cálculo
    :return: Melhor taxa livre de risco anualizada
    """
    selic = SELIC(anos_hist)
    ipca = IPCA(anos_hist)

    if ipca.media_ganho_real() > selic.media_anual():
        return ipca.media_ganho_real()

    return selic.media_anual()


def main():
    selic = SELIC(1)
    ipca = IPCA(1)

    print(f"Taxa SELIC atual: {selic.atual()}%")
    print(f"Média anual SELIC: {selic.media_anual()}%")
    print(f"Média anual SELIC líquida: {selic.media_ganho_real()}%")
    print(f"Média anual IPCA: {ipca.media_anual()}%")
    print(f"Média anual IPCA líquida: {ipca.media_ganho_real()}%")



if __name__ == "__main__":
    main()
