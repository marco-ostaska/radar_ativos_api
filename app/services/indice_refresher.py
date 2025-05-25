from datetime import datetime, timedelta
from app.db.banco_central_db import BancoCentralDB
from app.services.banco_central import SELIC, IPCA

class IndiceRefresher:
    """
    Serviço para gerenciar índices: busca no SQLite ou atualiza via Banco Central.
    """

    def __init__(self):
        self.repo = BancoCentralDB()
        self.cache_dias_valido = 30  # dias para considerar o cache válido

    def get_indices(self, force_update: bool = False) -> dict:
        """
        Obtém índices atualizados. Se necessário, atualiza a partir do Banco Central.

        :param force_update: Se True, força atualização dos dados do Banco Central
        :return: Dicionário com índices (selic, ipca, etc)
        """
        if not force_update:
            indices_dict = self.repo.get_indices()  # Novo formato: {indice: {valor, data_atualizacao}}
            if indices_dict:
                # Vamos pegar a data mais recente entre os índices
                datas = [datetime.strptime(v["data_atualizacao"], "%Y-%m-%d %H:%M:%S") for v in indices_dict.values() if v.get("data_atualizacao")]
                if datas:
                    data_cache = max(datas)
                    if datetime.now() - data_cache < timedelta(days=self.cache_dias_valido):
                        return {k: v["valor"] for k, v in indices_dict.items()}

        # Atualizar via API se necessário
        try:
            selic = SELIC(5)
            ipca = IPCA(5)
            ipca_atual = IPCA(1)

            novo_indices = {
                "selic": selic.media_ganho_real(),
                "selic_atual": selic.atual(),
                "ipca": ipca.media_ganho_real(),
                "ipca_media5": ipca.media_anual(),
                "ipca_atual": ipca_atual.media_anual(),
            }

            self.repo.save_indices(novo_indices)
            indices_atualizados = self.repo.get_indices()
            return {k: v["valor"] for k, v in indices_atualizados.items()}

        except Exception as e:
            raise RuntimeError(f"Erro ao atualizar índices: {str(e)}")

    def melhor_indice(self) -> float:
        """
        Retorna o melhor índice entre SELIC e IPCA armazenados.

        :return: Valor do melhor índice
        """
        indices = self.get_indices()
        return max(indices.get("selic", 0), indices.get("ipca", 0))

if __name__ == "__main__":
    refresher = IndiceRefresher()

    print("\n--- Teste: Buscar índices normais ---")
    indices = refresher.get_indices()
    print(indices)

    print("\n--- Teste: Buscar índices forçando atualização ---")
    indices_forcados = refresher.get_indices(force_update=True)
    print(indices_forcados)

    print("\n--- Teste: Melhor índice ---")
    melhor = refresher.melhor_indice()
    print(f"Melhor índice: {melhor}")
