# app/db/banco_central_db.py

from app.db.mongo import get_db
from datetime import datetime

class BancoCentralDB:
    """
    Acesso aos dados de índices do Banco Central na base MongoDB.
    """

    def __init__(self):
        self.collection = get_db()["indicadores"]  # Conecta na coleção 'indicadores'

    def get_indices(self):
        """
        Busca o documento de índices no banco de dados.

        :return: Documento dos índices (sem o campo _id)
        """
        return self.collection.find_one({"_id": "bc"}, {"_id": 0})

    def save_indices(self, data: dict):
        """
        Atualiza ou cria o documento de índices, usando sempre _id = 'bc'.

        :param data: Dicionário contendo os índices a salvar
        """
        data["_id"] = "bc"  # Garante _id fixo
        data["date"] = datetime.now().strftime("%Y-%m-%d")
        self.collection.replace_one({"_id": "bc"}, data, upsert=True)

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
