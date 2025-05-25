import sqlite3
from datetime import datetime
from app.db.sqlite import get_db

class BancoCentralDB:
    """
    Acesso aos dados de índices do Banco Central na base SQLite,
    com estrutura: indice (PK), valor, data_atualizacao.
    """

    def get_indices(self):
        """
        Busca todos os índices disponíveis no banco de dados.
        """
        conn = get_db()
        cur = conn.execute("SELECT * FROM indices_banco_central")
        rows = cur.fetchall()
        conn.close()
        return {row['indice']: {'valor': row['valor'], 'data_atualizacao': row['data_atualizacao']} for row in rows}

    def save_indices(self, data: dict):
        """
        Insere ou atualiza cada índice no banco de dados.
        """
        conn = get_db()
        data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for indice, valor in data.items():
            conn.execute("""
                INSERT OR REPLACE INTO indices_banco_central (indice, valor, data_atualizacao)
                VALUES (?, ?, ?)
            """, (indice, valor, data_atualizacao))
        conn.commit()
        conn.close()

# 🔥 Função de teste manual
def main():
    repo = BancoCentralDB()

    exemplo_indices = {
        "selic": 10.5,
        "selic_atual": 10.65,
        "ipca": 4.2,
        "ipca_media5": 4.5,
        "ipca_atual": 4.3,
    }
    print("Salvando índices de exemplo...")
    repo.save_indices(exemplo_indices)

    print("Buscando índices salvos...")
    indices = repo.get_indices()
    print(indices)

if __name__ == "__main__":
    main()
