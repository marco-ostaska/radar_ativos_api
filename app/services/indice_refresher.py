from datetime import datetime, timedelta
from app.services.banco_central import SELIC, IPCA
from app.utils.redis_cache import get_cached_data
import json

class IndiceRefresher:
    """
    Serviço para gerenciar índices: busca no Redis ou atualiza via Banco Central.
    """

    def __init__(self):
        self.cache_key = "indices_bcb"

    def get_indices(self, force_update: bool = False) -> dict:
        """
        Obtém índices do Redis, atualizando apenas se forçado.

        :param force_update: Se True, força atualização dos dados do Banco Central
        :return: Dicionário com índices (selic, ipca, etc)
        """
        def fetch_indices():
            selic = SELIC(5)
            ipca = IPCA(5)
            ipca_atual = IPCA(1)
            novo_indices = {
                "selic": selic.media_ganho_real(),
                "selic_atual": selic.atual(),
                "ipca": ipca.media_ganho_real(),
                "ipca_media5": ipca.media_anual(),
                "ipca_atual": ipca_atual.media_anual(),
                "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return novo_indices

        from app.utils.redis_cache import redis_client

        if not force_update:
            value = redis_client.get(self.cache_key)
            if value:
                print(f"[CACHE] HIT for {self.cache_key}")
                indices_dict = json.loads(value)
                return {k: v for k, v in indices_dict.items() if k != "data_atualizacao"}

        # Força atualização
        print(f"[CACHE] FORCE UPDATE for {self.cache_key}")
        indices_dict = fetch_indices()
        redis_client.set(self.cache_key, json.dumps(indices_dict))
        return {k: v for k, v in indices_dict.items() if k != "data_atualizacao"}

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
