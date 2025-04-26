from fastapi import APIRouter, HTTPException
from app.db.indicadores_ativos_db import IndicadoresAtivosDB

router = APIRouter(prefix="/indicadores/admin", tags=["Administração de Ativos"])

db = IndicadoresAtivosDB()

@router.post("/adicionar", summary="Adiciona um ativo a uma categoria")
def adicionar_ativo(tipo: str, ticker: str):
    """
    Adiciona um ticker a uma categoria de ativos.
    """
    tipo = tipo.lower()
    ticker = ticker.upper()

    categoria = db.collection.find_one({"_id": tipo})
    if not categoria:
        raise HTTPException(status_code=404, detail=f"Categoria '{tipo}' não encontrada.")

    tickers = set(categoria.get("tickers", []))
    if ticker in tickers:
        raise HTTPException(status_code=400, detail=f"Ticker '{ticker}' já existe na categoria '{tipo}'.")

    tickers.add(ticker)
    db.collection.update_one(
        {"_id": tipo},
        {"$set": {"tickers": sorted(list(tickers))}}
    )

    return {"message": f"Ticker '{ticker}' adicionado à categoria '{tipo}' com sucesso."}

@router.delete("/remover", summary="Remove um ativo de uma categoria")
def remover_ativo(tipo: str, ticker: str):
    """
    Remove um ticker de uma categoria de ativos.
    """
    tipo = tipo.lower()
    ticker = ticker.upper()

    categoria = db.collection.find_one({"_id": tipo})
    if not categoria:
        raise HTTPException(status_code=404, detail=f"Categoria '{tipo}' não encontrada.")

    tickers = set(categoria.get("tickers", []))
    if ticker not in tickers:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' não encontrado na categoria '{tipo}'.")

    tickers.remove(ticker)
    db.collection.update_one(
        {"_id": tipo},
        {"$set": {"tickers": sorted(list(tickers))}}
    )

    return {"message": f"Ticker '{ticker}' removido da categoria '{tipo}' com sucesso."}

@router.get("/listar", summary="Lista ativos de uma categoria")
def listar_ativos(tipo: str):
    """
    Lista todos os tickers de uma categoria de ativos.
    """
    tipo = tipo.lower()

    categoria = db.collection.find_one({"_id": tipo})
    if not categoria:
        raise HTTPException(status_code=404, detail=f"Categoria '{tipo}' não encontrada.")

    tickers = categoria.get("tickers", [])
    return {"categoria": tipo, "tickers": sorted(tickers)}

@router.get("/categorias", summary="Lista todas as categorias existentes")
def listar_categorias():
    """
    Lista todas as categorias disponíveis no banco de dados.
    """
    categorias = db.collection.distinct("_id")
    return {"categorias": sorted(categorias)}
