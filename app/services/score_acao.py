def score_trailing_pe(data) -> int:
    if 'trailingPE' in data.info:
        if data.info['trailingPE'] < 10:
            return 2
        if data.info['trailingPE'] < 20:
            return 1
    return 0


def score_price_to_book(data) -> int:
    if 'priceToBook' in data.info:
        if data.info['priceToBook'] < 1.5:
            return 2
        if data.info['priceToBook'] < 2:
            return 1
    return 0


def score_price_to_sales(data) -> int:
    if 'priceToSalesTrailing12Months' in data.info:
        if data.info['priceToSalesTrailing12Months'] < 2:
            return 2
        if data.info['priceToSalesTrailing12Months'] < 3:
            return 1
    return 0


def score_gross_margins(data) -> int:
    if 'grossMargins' in data.info:
        if data.info['grossMargins'] > 0.40:
            return 2
        if data.info['grossMargins'] > 0.30:
            return 1
    return 0


def score_operating_margins(data) -> int:
    if 'operatingMargins' in data.info:
        if data.info['operatingMargins'] > 0.30:
            return 2
        if data.info['operatingMargins'] > 0.20:
            return 1
    return 0


def score_profit_margins(data) -> int:
    if 'profitMargins' in data.info:
        if data.info['profitMargins'] > 0.20:
            return 2
        if data.info['profitMargins'] > 0.10:
            return 1
    return 0


def score_earnings_growth(data) -> int:
    if 'earningsGrowth' in data.info:
        if data.info['earningsGrowth'] > 0.20:
            return 2
        if data.info['earningsGrowth'] > 0.10:
            return 1
    return 0


def score_debt_to_ebitda(data) -> int:
    if 'totalDebt' in data.info and 'ebitda' in data.info:
        debt_to_ebitda = data.info['totalDebt'] / data.info['ebitda']
        if debt_to_ebitda < 2:
            return 2
        if debt_to_ebitda < 3:
            return 1
    return 0


def score_revenue_growth(data) -> int:
    if 'revenueGrowth' in data.info:
        if data.info['revenueGrowth'] > 0.10:
            return 2
        if data.info['revenueGrowth'] > 0.05:
            return 1
    return 0


def score_current_ratio(data) -> int:
    if 'currentRatio' in data.info:
        if data.info['currentRatio'] > 1.5:
            return 2
        if data.info['currentRatio'] > 1.0:
            return 1
    return 0


def score_quick_ratio(data) -> int:
    if 'quickRatio' in data.info:
        if data.info['quickRatio'] > 1:
            return 2
        if data.info['quickRatio'] > 0.5:
            return 1
    return 0


def score_dividend_yield(data, indice_base: float) -> int:
    if 'dividendYield' in data.info:
        if data.info['dividendYield'] > indice_base:
            return 2
        if data.info['dividendYield'] == indice_base:
            return 1
    return 0


def score_pay_out_ratio(data) -> int:
    if 'payoutRatio' in data.info and data.info['payoutRatio'] < 0.50:
        return 2
    return 0


def score_beta(data) -> int:
    if 'beta' in data.info and data.info['beta'] < 1:
        return 2
    return 0


def score_risco_geral(data) -> int:
    if 'overallRisk' not in data.info:
        return -2
    if data.info['overallRisk'] > 5:
        return -3
    if data.info['overallRisk'] == 1:
        return 2
    return 0


def score_free_float(data) -> int:
    if 'floatShares' not in data.info or 'sharesOutstanding' not in data.info:
        return 0
    if data.info['floatShares'] / data.info['sharesOutstanding'] * 100 > 30:
        return 2
    return 0


def score_earning_yield(data, indice_base: float) -> int:
    if 'trailingPE' not in data.info:
        return 0
    earning_yield = (1 / data.info['trailingPE']) * 100
    if earning_yield > indice_base:
        return 2
    return -2


def calculate_max_score() -> int:
    return 32  # Soma de todos scores possíveis


def evaluate_company(data, indice_base: float = 7) -> float:
    score = 0
    score += score_trailing_pe(data)
    score += score_price_to_book(data)
    score += score_price_to_sales(data)
    score += score_gross_margins(data)
    score += score_operating_margins(data)
    score += score_profit_margins(data)
    score += score_earnings_growth(data)
    score += score_debt_to_ebitda(data)
    score += score_revenue_growth(data)
    score += score_current_ratio(data)
    score += score_quick_ratio(data)
    score += score_dividend_yield(data, indice_base)
    score += score_pay_out_ratio(data)
    score += score_beta(data)
    score += score_risco_geral(data)
    score += score_free_float(data)
    score += score_earning_yield(data, indice_base)

    max_score = calculate_max_score()
    normalized_score = (score / max_score) * 10
    return round(normalized_score, 1)


def main():
    import yfinance as yf

    ativo = "CAML3.SA"
    data = yf.Ticker(ativo)

    nota = evaluate_company(data)
    print(f"Nota do ativo {ativo}: {nota}/10")


if __name__ == "__main__":
    main()
