from fastapi import APIRouter, HTTPException, Query

from app.services.indice_refresher import IndiceRefresher

router = APIRouter(prefix="/indices", tags=["Índices"])

refresher = IndiceRefresher()

@router.get("/atualiza", summary="Retorna índices armazenados ou atualiza se necessário")
def get_indices(force: bool = Query(False, description="Força atualização dos índices via Banco Central")):
    try:
        indices = refresher.get_indices(force_update=force)
        return indices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/melhor", summary="Retorna o melhor índice entre SELIC e IPCA")
def get_melhor_indice():
    try:
        melhor = refresher.melhor_indice()
        return {"melhor_indice": melhor}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    