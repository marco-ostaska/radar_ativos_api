from fastapi import APIRouter, HTTPException, Query

from app.services.fii_detalhe import FiiDetalhe

router = APIRouter(prefix="/fii", tags=["FII"])

fii_detalhe = FiiDetalhe()

@router.get("/radar", summary="Obtém dados simplificados do FII para radar de oportunidades")
def radar_fii(
    ticker: str = Query(..., description="Ticker do FII, ex: HGLG11"),
    # tipo: str = Query(..., description="Tipo do fundo: shopping, logistica, papel, hibrido, fiagro ou infra")
):
    try:
        dados = fii_detalhe.get_radar(ticker)
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detalhado", summary="Obtém dados detalhados do FII para análise completa")
def detalhado_fii(
    ticker: str = Query(..., description="Ticker do FII, ex: HGLG11"),
    # tipo: str = Query(..., description="Tipo do fundo: shopping, logistica, papel, hibrido, fiagro ou infra")
):
    try:
        dados = fii_detalhe.get_detalhado(ticker)
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
