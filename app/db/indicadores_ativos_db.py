import sqlite3
from app.db.sqlite import get_db

class IndicadoresAtivosDB:
    """
    Banco de dados para buscar spreads, risco e tickers de tipos de ativos.
    """

    def get_spread(self, tipo: str) -> float | None:
        conn = get_db()
        cur = conn.execute("SELECT spread FROM tipos WHERE tipo = ?", (tipo,))
        row = cur.fetchone()
        conn.close()
        return row['spread'] if row else None

    def get_risco(self, tipo: str) -> int | None:
        conn = get_db()
        cur = conn.execute("SELECT risco_operacional FROM tipos WHERE tipo = ?", (tipo,))
        row = cur.fetchone()
        conn.close()
        return row['risco_operacional'] if row else None

    def get_tickers(self, tipo: str) -> list:
        conn = get_db()
        cur = conn.execute("SELECT ticker FROM ativos WHERE tipo = ?", (tipo,))
        tickers = [row['ticker'] for row in cur.fetchall()]
        conn.close()
        return tickers

def main():
    db = IndicadoresAtivosDB()

    tipo = "logistica"

    print(f"Buscando spread e risco da categoria '{tipo}'...")
    spread = db.get_spread(tipo)
    risco = db.get_risco(tipo)
    print(f"Spread: {spread}")
    print(f"Risco: {risco}")

    print(f"Buscando tickers da categoria '{tipo}'...")
    tickers = db.get_tickers(tipo)
    print(f"Tickers: {tickers}")

if __name__ == "__main__":
    main()
