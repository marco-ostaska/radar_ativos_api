import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Aqui agora não tem valor default — se não setar a env, quebra
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_URI or not MONGO_DB:
    raise RuntimeError("Variáveis de ambiente MONGO_URI ou MONGO_DB não configuradas!")

client = MongoClient(MONGO_URI)

def get_db():
    """
    Retorna a instância do banco de dados.
    """
    return client[MONGO_DB]
