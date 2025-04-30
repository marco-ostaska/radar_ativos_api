from app.services.fii import FII


def score_dy(fii_data: FII, indice_base: float) -> int:
    """
    Score baseado no Dividend Yield comparado ao índice base.
    """
    if fii_data.dividend_yield > (indice_base + 3) / 100:
        return 2
    if fii_data.dividend_yield == indice_base / 100:
        return 1
    return 0


def score_preco_medio(fii_data: FII) -> int:
    """
    Score baseado na relação entre o preço atual, preço médio e máxima de 52 semanas.
    """
    if 'currentPrice' not in fii_data.info or 'fiftyDayAverage' not in fii_data.info or 'fiftyTwoWeekHigh' not in fii_data.info:
        return 0

    score = 0
    if fii_data.cotacao > fii_data.info['fiftyTwoWeekHigh'] * 0.90:
        score += 1
    if fii_data.cotacao < fii_data.info['fiftyDayAverage']:
        score += 1
    return score


def score_market_cap(fii_data: FII) -> int:
    """
    Score baseado no valor de mercado do fundo.
    """
    if 'marketCap' not in fii_data.info:
        return 0

    market_cap = fii_data.info['marketCap']
    if market_cap > 1e9:
        return 2
    if market_cap > 5e8:
        return 1
    return 0


def score_volume_medio(fii_data: FII) -> int:
    """
    Score baseado no volume médio de negociações.
    """
    if 'averageVolume' not in fii_data.info:
        return 0

    if fii_data.info['averageVolume'] > 50000:
        return 1
    return 0


def score_dividendos_crescentes(fii_data: FII, indice_base: float) -> int:
    """
    Score baseado na consistência dos dividendos acima do índice base.
    """
    if fii_data.dividend_yield > (indice_base + 3) / 100:
        return 2
    if fii_data.dividend_yield > (indice_base + 1) / 100:
        return 1
    return 0


def score_vpa(fii_data: FII) -> int:
    """
    Score baseado na relação entre o VPA e a cotação.
    """
    if fii_data.vpa > fii_data.cotacao:
        return 1
    if fii_data.vpa == fii_data.cotacao:
        return 0
    return -2


def bazin_score(fii_data: FII, indice_base: float) -> int:
    """
    Score baseado no preço teto do método Bazin.
    """
    if fii_data.cotacao < fii_data.dividendo_estimado / (indice_base + 3) * 100:
        return 1
    return -1


def calculate_max_score() -> int:
    """
    Calcula a pontuação máxima possível para normalizar o score final.
    """
    return (
        2  # score_dy
        + 2  # score_preco_medio
        + 2  # score_market_cap
        + 1  # score_volume_medio
        + 2  # score_dividendos_crescentes
        + 1  # score_vpa
        + 1  # bazin_score
    )


def evaluate_fii(fii_data: FII, indice_base: float) -> float:
    """
    Avalia o FII com base em vários critérios e retorna um score de 0 a 10.
    """
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
    """
    Teste local da avaliação de um FII.
    """
    fii_data = FII('HSLG11.SA')
    fii_score = evaluate_fii(fii_data, 7.5)  # Supondo índice base 7% real
    print(f"Nota do FII {fii_data.ticker}: {fii_score}/10")


if __name__ == "__main__":
    main()
