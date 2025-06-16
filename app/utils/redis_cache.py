import redis
import json
import logging
import pandas as pd

# Conexão com Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def _safe_dict(df: pd.DataFrame) -> dict:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    else:
        df.columns = df.columns.map(str)
    df.index = df.index.map(str)
    return df.to_dict(orient="index")

def _safe_series(s: pd.Series) -> dict:
    s = s.copy()
    s.index = s.index.map(str)
    return s.to_dict()

def serialize(obj):
    if isinstance(obj, pd.DataFrame):
        return _safe_dict(obj)
    elif isinstance(obj, pd.Series):
        return _safe_series(obj)
    elif isinstance(obj, dict):
        return {
            str(k): serialize(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    else:
        try:
            if pd.isna(obj):
                return None
        except Exception:
            pass
    return obj

def get_cached_data(key: str, ttl: int, fetch_fn):
    value = redis_client.get(key)
    if value:
        print(f"[CACHE] HIT for {key}")
        return json.loads(value)

    print(f"[CACHE] MISS for {key}")
    result = fetch_fn()

    if isinstance(result, dict):
        result = serialize(result)

    print(f"[CACHE] SET for {key}")
    redis_client.setex(key, ttl, json.dumps(result))
    return result
