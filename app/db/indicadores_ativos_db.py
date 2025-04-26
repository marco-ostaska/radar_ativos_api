from app.db.mongo import get_db

class IndicadoresAtivosDB:
    """
    Banco de dados para buscar spreads e tickers de categorias de ativos (FIIs, ações, etc).
    """

    def __init__(self):
        self.collection = get_db()["indicadores"]

    def get_spread(self, tipo: str) -> float | None:
        categoria = self.collection.find_one({"_id": tipo})
        return categoria.get("spread") if categoria else None

    def get_tickers(self, tipo: str) -> list:
        categoria = self.collection.find_one({"_id": tipo})
        return categoria.get("tickers", []) if categoria else []

def main():
    db = IndicadoresAtivosDB()

    tipo = "logistica"

    print(f"Buscando spread da categoria '{tipo}'...")
    spread = db.get_spread(tipo)
    print(f"Spread: {spread}")

    print(f"Buscando tickers da categoria '{tipo}'...")
    tickers = db.get_tickers(tipo)
    print(f"Tickers: {tickers}")

if __name__ == "__main__":
    main()
