from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import acoes_router, fii_router, indicadores_admin_router, indices_router

app = FastAPI(
    title="Radar Ativos API",
    description="API para análise de ações e FIIs",
    version="1.0.0"
)

# 🔓 Libera requisições do front-end React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Ou ["*"] se quiser liberar tudo no dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Rotas
app.include_router(acoes_router.router)
app.include_router(fii_router.router)
app.include_router(indices_router.router)
app.include_router(indicadores_admin_router.router)
