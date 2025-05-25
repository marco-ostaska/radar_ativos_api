from fastapi import APIRouter, HTTPException
from app.db.indicadores_ativos_db import IndicadoresAtivosDB
from app.db.sqlite import get_db  # Importa get_db diretamente para conexões

router = APIRouter(prefix="/indicadores/admin", tags=["Administração de Ativos"])

db = IndicadoresAtivosDB()

@router.post("/adicionar", summary="Adiciona um ativo a uma categoria")
def adicionar_ativo(tipo: str, ticker: str):
    tipo = tipo.lower()
    ticker = ticker.upper()

    # Verifica se a categoria (tipo) existe na tabela tipos
    spread = db.get_spread(tipo)
    if spread is None:
        raise HTTPException(status_code=404, detail=f"Categoria '{tipo}' não encontrada.")

    # Verifica se o ticker já existe na tabela ativos
    tickers = db.get_tickers(tipo)
    if ticker in tickers:
        raise HTTPException(status_code=400, detail=f"Ticker '{ticker}' já existe na categoria '{tipo}'.")

    # Adiciona o ticker à tabela ativos
    conn = get_db()
    conn.execute("INSERT INTO ativos (ticker, tipo) VALUES (?, ?)", (ticker, tipo))
    conn.commit()
    conn.close()

    return {"message": f"Ticker '{ticker}' adicionado à categoria '{tipo}' com sucesso."}

@router.delete("/remover", summary="Remove um ativo de uma categoria")
def remover_ativo(tipo: str, ticker: str):
    tipo = tipo.lower()
    ticker = ticker.upper()

    # Verifica se o ticker existe na tabela ativos
    tickers = db.get_tickers(tipo)
    if ticker not in tickers:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' não encontrado na categoria '{tipo}'.")

    # Remove o ticker
    conn = get_db()
    conn.execute("DELETE FROM ativos WHERE ticker = ? AND tipo = ?", (ticker, tipo))
    conn.commit()
    conn.close()

    return {"message": f"Ticker '{ticker}' removido da categoria '{tipo}' com sucesso."}

@router.get("/listar", summary="Lista ativos de uma categoria")
def listar_ativos(tipo: str):
    tipo = tipo.lower()

    spread = db.get_spread(tipo)
    if spread is None:
        raise HTTPException(status_code=404, detail=f"Categoria '{tipo}' não encontrada.")

    tickers = db.get_tickers(tipo)
    return {"categoria": tipo, "tickers": sorted(tickers)}

@router.get("/categorias", summary="Lista todas as categorias existentes")
def listar_categorias():
    conn = get_db()
    cur = conn.execute("SELECT tipo FROM tipos")
    categorias = [row['tipo'] for row in cur.fetchall()]
    conn.close()
    return {"categorias": sorted(categorias)}
