from fastapi import APIRouter, HTTPException, Query

from app.services.fii import FII

router = APIRouter(prefix="/fii", tags=["FII"])



@router.get("/radar", summary="Obtém dados simplificados do FII para radar de oportunidades")
def radar_fii(
    ticker: str = Query(..., description="Ticker do FII, ex: HGLG11"),
    force: bool = Query(False, description="Força atualização dos dados ignorando o cache")
):
    try:
        fii = FII(ticker,force_update=force)
        dados = fii.get_radar()
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/detalhado", summary="Obtém dados detalhados do FII para análise completa")
# def detalhado_fii(
#     ticker: str = Query(..., description="Ticker do FII, ex: HGLG11"),
#     # tipo: str = Query(..., description="Tipo do fundo: shopping, logistica, papel, hibrido, fiagro ou infra")
# ):
#     try:
#         dados = fii_detalhe.get_detalhado(ticker)
#         return dados
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
