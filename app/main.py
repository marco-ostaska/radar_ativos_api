from fastapi import FastAPI
from app.routers import acoes_router, fii_router, indicadores_admin_router, indices_router

app = FastAPI(
    title="Radar Ativos API",
    description="API para análise de ações e FIIs",
    version="1.0.0"
)

app.include_router(acoes_router.router)
app.include_router(fii_router.router)
app.include_router(indices_router.router)
app.include_router(indicadores_admin_router.router)
