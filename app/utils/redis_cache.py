import redis
import json
import logging
import pandas as pd

# Configura o log (opcional)
# logging.basicConfig(level=logging.DEBUG)

# Conexão com Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def _safe_dict(df: pd.DataFrame) -> dict:
    """Transforma DataFrame em dicionário seguro para json/Redis"""
    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    else:
        df.columns = df.columns.map(str)

    df.index = df.index.map(str)  # evita erro com Timestamp
    return df.to_dict(orient="index")

def get_cached_data(key: str, ttl: int, fetch_fn):
    """
    Consulta o Redis. Se não houver cache, executa fetch_fn() e armazena resultado por ttl segundos.
    """
    value = redis_client.get(key)
    if value:
        logging.debug(f"Cache hit: {key}")
        return json.loads(value)

    logging.debug(f"Cache miss: {key}")
    result = fetch_fn()

    # Se o resultado for um dict contendo DataFrame(s), serializa eles
    def serialize(obj):
        if isinstance(obj, pd.DataFrame):
            return _safe_dict(obj)
        return obj

    if isinstance(result, dict):
        result = {k: serialize(v) for k, v in result.items()}

    redis_client.setex(key, ttl, json.dumps(result))
    return result
